// 真实搜索结果 - 从API响应中提取
const searchResults = {
  "理财": {"count": 22, "feeds": [{"id":"695b1a7d000000001e00ce3c","xsecToken":"ABMebxtKoa2sfDXhNyGoQvFDDjWi7MLQor9LT3wMhxxiw=","userId":"5a62ff6711be102e867a6e11","nickname":"芋泥","likedCount":"127167"},{"id":"6959e5b6000000001f00df0a","xsecToken":"ABvrv3GfWtbUGdXQ1QAoXEeNlnw9aORA0Y7PNpt-Yx4SE=","userId":"68941a2a000000002803729d","nickname":"中安在线","likedCount":"2555"},{"id":"695a663f00000000220090eb","xsecToken":"ABJ6xfbzrZ-panCMlPfaCtktmOHyWcbd2lhGGWOYgBHbQ=","userId":"669b1f19000000002402254f","nickname":"钱途晓保","likedCount":"1557"}]},
  "基金": {"count": 22, "feeds": [{"id":"695a57c7000000001e00e45f","xsecToken":"ABJ6xfbzrZ-panCMlPfaCtkvX0oM9F--BLi-XUgIelOf4=","userId":"655369a00000000002010829","nickname":"小面包","likedCount":"28608"},{"id":"695a1b8c00000000220302c1","xsecToken":"ABJ6xfbzrZ-panCMlPfaCtkhYGnsk6R3SWOlGh51S7D6Y=","userId":"690ee7a4000000003702ab46","nickname":"煎饼狗子","likedCount":"20053"},{"id":"6959f93b000000001e028f42","xsecToken":"ABvrv3GfWtbUGdXQ1QAoXEeLYTNQ8Piy_rA0-1P3mzzA4=","userId":"5b877f40304bcc0001af2845","nickname":"金富江Kimdelvey","likedCount":"16083"}]},
  "股票": {"count": 22, "feeds": [{"id":"69548f2d000000001e03b150","xsecToken":"ABn2Z5Y4D7koMMohim4fxAl_y3xTK9hUS68d-gl2E4jB0=","userId":"6194ae1a000000002102497a","nickname":"奶爸财经","likedCount":"14663"},{"id":"6953895b000000001f00e231","xsecToken":"AB2XrCgthEqasbeLiEoXb62yVwurOGlWR8vu06a6KMTXo=","userId":"68e4ce0a0000000037000157","nickname":"爱学习的叮当猫","likedCount":"11729"}]},
  "副业": {"count": 22, "feeds": [{"id":"6953a0a8000000001e016166","xsecToken":"AB2XrCgthEqasbeLiEoXb62_vPN89mmPpXeVbc0JQ96-s=","userId":"5c2aec6c000000000600c4de","nickname":"一粒大眼儿","likedCount":"10535"},{"id":"6954c63f000000001e03b23a","xsecToken":"ABn2Z5Y4D7koMMohim4fxAl8WsBSvp9CtcYbcgOpDTlEI=","userId":"58c8d26d6a6a6933d30c849d","nickname":"今天你美式了吗","likedCount":"7712"}]},
  "搞钱": {"count": 22, "feeds": [{"id":"69561d48000000001d03a7ce","xsecToken":"AB-ZJRJ1xe3uPcvcaS35RlWreem5UMaM_Wuz2LK2db0Kg=","userId":"660ee4ee000000000d0264d6","nickname":"渔山学财经","likedCount":"3159"}]},
  "存钱": {"count": 22, "feeds": [{"id":"6958afdb000000001f00aaec","xsecToken":"ABi02UEDFPWIHOTR1EwbbTmnWGf4c09EHJqUoNrlusAQk=","userId":"6069b265000000000100233b","nickname":"迟迟","likedCount":"8366"},{"id":"6957938e0000000022031466","xsecToken":"ABU1BHhdnkQPZBoV2fmsVTRIH81wOTxBYHfxAcEqQ5fOs=","userId":"6669a7f10000000003033f08","nickname":"天生好命","likedCount":"6981"}]},
  "宏观经济": {"count": 22, "feeds": [{"id":"6955ec10000000001e00c8f5","xsecToken":"ABKWMlJgRPt_5ijvcgFTqbgI1y2dN1_oZkA0nbw7YRh_4=","userId":"600e6c880000000001007326","nickname":"财经姚钱术","likedCount":"2690"}]},
  "黄金": {"count": 22, "feeds": [{"id":"695490ca000000002202fde4","xsecToken":"ABn2Z5Y4D7koMMohim4fxAl-WUSRJsD0rl98MWH8EN0AY=","userId":"6045d07d000000000100911f","nickname":"周六福产品在线","likedCount":"10511"}]},
  "A股": {"count": 21, "feeds": [{"id":"6957c7f2000000001d03ee81","xsecToken":"ABU1BHhdnkQPZBoV2fmsVTRGckftdOuV_439T1x_zzFrw=","userId":"660ee4ee000000000d0264d6","nickname":"渔山学财经","likedCount":"8254"}]},
  "保险": {"count": 22, "feeds": [{"id":"695b1a7d000000001e00ce3c","xsecToken":"ABMebxtKoa2sfDXhNyGoQvFDDjWi7MLQor9LT3wMhxxiw=","userId":"5a62ff6711be102e867a6e11","nickname":"芋泥","likedCount":"127167"}]}
};

const userMap = new Map();
const allFeeds = [];
const keywords = Object.keys(searchResults);

keywords.forEach(keyword => {
  const result = searchResults[keyword];
  result.feeds.forEach(feed => {
    if (feed.userId) {
      const uid = feed.userId;
      if (!userMap.has(uid)) {
        userMap.set(uid, {
          userId: uid,
          nickname: feed.nickname,
          xsecTokens: new Set(),
          keywords: new Set()
        });
      }
      userMap.get(uid).xsecTokens.add(feed.xsecToken);
      userMap.get(uid).keywords.add(keyword);

      allFeeds.push({
        id: feed.id,
        xsecToken: feed.xsecToken,
        userId: uid,
        nickname: feed.nickname,
        likedCount: parseInt(feed.likedCount || '0'),
        keyword: keyword
      });
    }
  });
});

const users = Array.from(userMap.entries()).map(([uid, data]) => ({
  userId: uid,
  nickname: data.nickname,
  xsecToken: Array.from(data.xsecTokens)[0],
  keywords: Array.from(data.keywords)
}));

// 输出结果
const output = {
  total_feeds: allFeeds.length,
  unique_users: userMap.size,
  keywords: keywords,
  users: users,
  all_feeds: allFeeds
};

console.log(JSON.stringify(output, null, 2));
