# -*- coding: UTF-8 -*-

_RANK ={
  "Rank": {
    "table": [
      {
        "-ID": "1",
        "-RankTop": "1",
        "-RankLast": "1",
        "-CoinReward": "5000",
        "-DiamondReward": "800"
      },
      {
        "-ID": "2",
        "-RankTop": "2",
        "-RankLast": "2",
        "-CoinReward": "2000",
        "-DiamondReward": "600"
      },
      {
        "-ID": "3",
        "-RankTop": "3",
        "-RankLast": "3",
        "-CoinReward": "1000",
        "-DiamondReward": "400"
      },
      {
        "-ID": "4",
        "-RankTop": "4",
        "-RankLast": "30",
        "-CoinReward": "750",
        "-DiamondReward": "200"
      },
      {
        "-ID": "5",
        "-RankTop": "31",
        "-RankLast": "100",
        "-CoinReward": "500",
        "-DiamondReward": "100"
      },
      {
        "-ID": "6",
        "-RankTop": "101",
        "-RankLast": "10000",
        "-CoinReward": "250",
        "-DiamondReward": "50"
      }
    ]
  }
}

RANK = _RANK['Rank']['table']
for v in RANK:
    v['-RankTop'] = int(v['-RankTop'])
    v['-RankLast'] = int(v['-RankLast'])
    v['-CoinReward'] = int(v['-CoinReward'])
    v['-DiamondReward'] = int(v['-DiamondReward'])
