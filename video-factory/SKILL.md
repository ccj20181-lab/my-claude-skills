# Video Factory Skill

A modular, template-based video generation factory that decouples content logic from visual presentation.
Uses Python for orchestration and Remotion (React) for rendering.

## Usage

```bash
# Create a new video project
run_skill video-factory create --topic "My Topic" --template "knowledge-explainer" --output ./my-video

# Generate assets for an existing project
run_skill video-factory gen-assets --project ./my-video
```

## Templates

### knowledge-explainer
The classic "Miaodong" style finance explainer.
- 3:4 Vertical Video (1080x1440)
- Structure: Title -> Content Scenes -> Summary -> Ending

## Architecture

- **Core Engine**: Python scripts in `scripts/engine`
- **Templates**: Located in `templates/`
- **Output**: Standard Remotion projects
