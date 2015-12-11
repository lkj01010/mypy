# -*- coding: UTF-8 -*-

_RANK ={
  "Rank": {
    "table": [
      {
        "-ID": "1",
        "-RankTop": "1",
        "-RankLast": "1",
        "-CoinReward": "10000",
        "-DiamondReward": "800"
      },
      {
        "-ID": "2",
        "-RankTop": "2",
        "-RankLast": "2",
        "-CoinReward": "9000",
        "-DiamondReward": "700"
      },
      {
        "-ID": "3",
        "-RankTop": "3",
        "-RankLast": "3",
        "-CoinReward": "8000",
        "-DiamondReward": "650"
      },
      {
        "-ID": "4",
        "-RankTop": "4",
        "-RankLast": "4",
        "-CoinReward": "7000",
        "-DiamondReward": "600"
      },
      {
        "-ID": "5",
        "-RankTop": "5",
        "-RankLast": "5",
        "-CoinReward": "6500",
        "-DiamondReward": "550"
      },
      {
        "-ID": "6",
        "-RankTop": "6",
        "-RankLast": "6",
        "-CoinReward": "6000",
        "-DiamondReward": "500"
      },
      {
        "-ID": "7",
        "-RankTop": "7",
        "-RankLast": "7",
        "-CoinReward": "5500",
        "-DiamondReward": "450"
      },
      {
        "-ID": "8",
        "-RankTop": "8",
        "-RankLast": "8",
        "-CoinReward": "5000",
        "-DiamondReward": "400"
      },
      {
        "-ID": "9",
        "-RankTop": "9",
        "-RankLast": "9",
        "-CoinReward": "4500",
        "-DiamondReward": "350"
      },
      {
        "-ID": "10",
        "-RankTop": "10",
        "-RankLast": "10",
        "-CoinReward": "4000",
        "-DiamondReward": "300"
      },
      {
        "-ID": "11",
        "-RankTop": "11",
        "-RankLast": "15",
        "-CoinReward": "3500",
        "-DiamondReward": "200"
      },
      {
        "-ID": "12",
        "-RankTop": "16",
        "-RankLast": "20",
        "-CoinReward": "3000",
        "-DiamondReward": "150"
      },
      {
        "-ID": "13",
        "-RankTop": "21",
        "-RankLast": "25",
        "-CoinReward": "2500",
        "-DiamondReward": "100"
      },
      {
        "-ID": "14",
        "-RankTop": "26",
        "-RankLast": "30",
        "-CoinReward": "2000",
        "-DiamondReward": "75"
      },
      {
        "-ID": "15",
        "-RankTop": "31",
        "-RankLast": "100",
        "-CoinReward": "1500",
        "-DiamondReward": "50"
      },
      {
        "-ID": "16",
        "-RankTop": "101",
        "-RankLast": "1000000000",
        "-CoinReward": "1000",
        "-DiamondReward": "10"
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
