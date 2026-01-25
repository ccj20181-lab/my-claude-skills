#!/usr/bin/env python3
"""
GitHub Pages Auto-Deploy Script
Handles HTML report generation, metadata updates, and Git automation

This script:
1. Generates HTML reports using the html_template module
2. Updates metadata.json with history records
3. Performs Git add/commit/push automatically
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add scripts directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from html_template import generate_report_html


# Default configuration
DEFAULT_DEPLOY_DIR = "/Users/henry/gh-pages-deploy"
DEFAULT_BRANCH = "gh-pages"
MAX_RETRY_COUNT = 3
GIT_TIMEOUT = 60  # seconds


class DeployError(Exception):
    """Custom exception for deployment errors."""
    pass


def log_info(msg: str) -> None:
    """Log info message."""
    print(f"[INFO] {msg}")


def log_success(msg: str) -> None:
    """Log success message."""
    print(f"[SUCCESS] {msg}")


def log_warn(msg: str) -> None:
    """Log warning message."""
    print(f"[WARN] {msg}")


def log_error(msg: str) -> None:
    """Log error message."""
    print(f"[ERROR] {msg}")


def run_git_command(
    args: List[str],
    cwd: str,
    timeout: int = GIT_TIMEOUT,
    check: bool = True
) -> Tuple[bool, str]:
    """
    Execute a git command with error handling.

    Args:
        args: Git command arguments (without 'git' prefix)
        cwd: Working directory
        timeout: Command timeout in seconds
        check: Whether to raise exception on failure

    Returns:
        Tuple of (success, output/error_message)
    """
    cmd = ['git'] + args
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check
        )
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s"
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() or str(e)
    except Exception as e:
        return False, str(e)


def validate_deploy_dir(deploy_dir: str) -> bool:
    """
    Validate that the deploy directory exists and is a git repository.

    Args:
        deploy_dir: Path to deployment directory

    Returns:
        True if valid, False otherwise
    """
    if not os.path.isdir(deploy_dir):
        log_error(f"Deploy directory does not exist: {deploy_dir}")
        return False

    git_dir = os.path.join(deploy_dir, '.git')
    if not os.path.isdir(git_dir):
        log_error(f"Not a git repository: {deploy_dir}")
        return False

    return True


def update_metadata(
    deploy_dir: str,
    report_filename: str,
    feeds: List[Dict[str, Any]],
    analysis: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Update metadata.json with new report information.

    Args:
        deploy_dir: Path to deployment directory
        report_filename: Name of the generated report file
        feeds: List of viral note data
        analysis: Optional analysis results

    Returns:
        True if successful, False otherwise
    """
    metadata_path = os.path.join(deploy_dir, 'data', 'metadata.json')

    # Ensure data directory exists
    data_dir = os.path.dirname(metadata_path)
    os.makedirs(data_dir, exist_ok=True)

    # Load existing metadata or create new
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {
                "version": "1.0.0",
                "total_reports": 0,
                "history": []
            }
    except json.JSONDecodeError:
        log_warn("Corrupted metadata.json, creating new one")
        metadata = {
            "version": "1.0.0",
            "total_reports": 0,
            "history": []
        }

    # Calculate statistics
    now = datetime.now()
    total_notes = len(feeds)
    total_likes = sum(f.get('likes', 0) for f in feeds)
    avg_likes = total_likes // max(total_notes, 1)
    total_followers = sum(f.get('followers', 0) for f in feeds)
    avg_followers = total_followers // max(total_notes, 1)
    top_viral_score = max((f.get('viral_score', 0) for f in feeds), default=0)

    # Extract date from filename
    date_part = report_filename.replace('report-', '').replace('.html', '')

    # Create new history entry
    new_entry = {
        "date": date_part,
        "filename": report_filename,
        "total_notes": total_notes,
        "avg_likes": avg_likes,
        "top_topic": analysis.get('top_topic', 'Finance') if analysis else 'Finance',
        "generated_at": now.isoformat()
    }

    # Update metadata
    metadata["generated_at"] = now.isoformat()
    metadata["total_notes"] = total_notes
    metadata["avg_likes"] = avg_likes
    metadata["avg_followers"] = avg_followers
    metadata["top_viral_score"] = round(top_viral_score, 2)
    metadata["latest_report"] = report_filename
    metadata["total_reports"] = metadata.get("total_reports", 0) + 1

    # Append to history (avoid duplicates)
    existing_filenames = {h.get('filename') for h in metadata.get('history', [])}
    if report_filename not in existing_filenames:
        if 'history' not in metadata:
            metadata['history'] = []
        metadata['history'].append(new_entry)

    # Write updated metadata
    try:
        # Write to temp file first for atomic operation
        temp_path = metadata_path + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # Rename temp file to actual file (atomic on POSIX)
        shutil.move(temp_path, metadata_path)
        log_success(f"Metadata updated: {metadata_path}")
        return True
    except Exception as e:
        log_error(f"Failed to update metadata: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False


def git_deploy(
    deploy_dir: str,
    report_filename: str,
    branch: str = DEFAULT_BRANCH
) -> bool:
    """
    Perform Git add, commit, and push operations.

    Args:
        deploy_dir: Path to deployment directory
        report_filename: Name of the report file to commit
        branch: Git branch to push to

    Returns:
        True if successful, False otherwise
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto update: {timestamp}"

    # Stage files
    files_to_add = [
        f"reports/{report_filename}",
        "data/metadata.json"
    ]

    for file_path in files_to_add:
        full_path = os.path.join(deploy_dir, file_path)
        if os.path.exists(full_path):
            success, msg = run_git_command(['add', file_path], deploy_dir)
            if not success:
                log_warn(f"Failed to stage {file_path}: {msg}")
        else:
            log_warn(f"File not found, skipping: {full_path}")

    # Check if there are changes to commit
    success, status = run_git_command(['status', '--porcelain'], deploy_dir)
    if success and not status.strip():
        log_info("No changes to commit")
        return True

    # Commit changes
    success, msg = run_git_command(['commit', '-m', commit_msg], deploy_dir)
    if not success:
        if "nothing to commit" in msg.lower():
            log_info("No changes to commit")
            return True
        log_error(f"Git commit failed: {msg}")
        return False

    log_success("Git commit successful")

    # Push to remote with retry
    for attempt in range(1, MAX_RETRY_COUNT + 1):
        log_info(f"Pushing to remote (attempt {attempt}/{MAX_RETRY_COUNT})...")
        success, msg = run_git_command(
            ['push', 'origin', branch],
            deploy_dir,
            timeout=GIT_TIMEOUT
        )

        if success:
            log_success(f"Git push successful to {branch}")
            return True
        else:
            log_warn(f"Push attempt {attempt} failed: {msg}")
            if attempt < MAX_RETRY_COUNT:
                log_info("Retrying...")

    log_error(f"Git push failed after {MAX_RETRY_COUNT} attempts")
    return False


def deploy_dashboard(
    feeds: List[Dict[str, Any]],
    analysis: Optional[Dict[str, Any]] = None,
    deploy_dir: str = DEFAULT_DEPLOY_DIR,
    branch: str = DEFAULT_BRANCH,
    skip_push: bool = False
) -> Tuple[bool, str]:
    """
    Complete deployment workflow.

    Args:
        feeds: List of viral note data
        analysis: Optional analysis results
        deploy_dir: Path to deployment directory
        branch: Git branch for deployment
        skip_push: If True, skip git push (for testing)

    Returns:
        Tuple of (success, report_filename or error_message)
    """
    log_info("Starting GitHub Pages deployment...")

    # Validate deploy directory
    if not validate_deploy_dir(deploy_dir):
        return False, f"Invalid deploy directory: {deploy_dir}"

    # Generate HTML report
    try:
        reports_dir = os.path.join(deploy_dir, "reports")
        report_filename = generate_report_html(feeds, analysis, reports_dir)
        log_success(f"HTML report generated: {report_filename}")
    except Exception as e:
        log_error(f"Failed to generate HTML report: {e}")
        return False, str(e)

    # Update metadata
    if not update_metadata(deploy_dir, report_filename, feeds, analysis):
        log_warn("Metadata update failed, continuing with git operations...")

    # Git deploy
    if skip_push:
        log_info("Skipping git push (test mode)")
        return True, report_filename

    if git_deploy(deploy_dir, report_filename, branch):
        log_success(f"Deployment complete! Report: {report_filename}")
        return True, report_filename
    else:
        log_warn("Git operations failed, but local files are saved")
        return True, report_filename  # Still return success if files are saved


def deploy_from_json(
    json_path: str,
    deploy_dir: str = DEFAULT_DEPLOY_DIR,
    branch: str = DEFAULT_BRANCH
) -> Tuple[bool, str]:
    """
    Deploy from a JSON data file.

    Args:
        json_path: Path to JSON file with feeds data
        deploy_dir: Path to deployment directory
        branch: Git branch for deployment

    Returns:
        Tuple of (success, report_filename or error_message)
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return False, f"Failed to read JSON file: {e}"

    feeds = data.get('feeds', data.get('notes', data if isinstance(data, list) else []))
    analysis = data.get('analysis', None)

    return deploy_dashboard(feeds, analysis, deploy_dir, branch)


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Deploy XHS Viral Report to GitHub Pages'
    )
    parser.add_argument(
        '--json',
        type=str,
        help='Path to JSON data file'
    )
    parser.add_argument(
        '--deploy-dir',
        type=str,
        default=DEFAULT_DEPLOY_DIR,
        help=f'Deployment directory (default: {DEFAULT_DEPLOY_DIR})'
    )
    parser.add_argument(
        '--branch',
        type=str,
        default=DEFAULT_BRANCH,
        help=f'Git branch (default: {DEFAULT_BRANCH})'
    )
    parser.add_argument(
        '--skip-push',
        action='store_true',
        help='Skip git push (for testing)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run with test data'
    )

    args = parser.parse_args()

    if args.test:
        # Test with sample data
        sample_feeds = [
            {
                "id": "test123",
                "title": "Test Note",
                "author": "Test Author",
                "likes": 5000,
                "followers": 1000,
                "viral_score": 25.5,
            }
        ]
        success, result = deploy_dashboard(
            sample_feeds,
            deploy_dir=args.deploy_dir,
            branch=args.branch,
            skip_push=args.skip_push
        )
    elif args.json:
        success, result = deploy_from_json(
            args.json,
            args.deploy_dir,
            args.branch
        )
    else:
        print("Error: Please provide --json or --test argument")
        parser.print_help()
        sys.exit(1)

    if success:
        print(f"\n{'='*50}")
        print(f"Deployment successful!")
        print(f"Report: {result}")
        print(f"URL: https://ccj20181-lab.github.io/xhs-viral-report/")
        print(f"{'='*50}")
    else:
        print(f"\nDeployment failed: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()
