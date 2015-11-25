# -*- coding: UTF-8 -*-

_GRADE = {
  "Grade": {
    "table": [
      {
        "-ID": "1",
        "-Name": "斥候",
        "-HonorMin": "0",
        "-HonorMax": "530",
        "-CoinReward": "1000",
        "-DiamondReward": "50",
        "-CardReward": "1#1#2"
      },
      {
        "-ID": "2",
        "-Name": "士兵",
        "-HonorMin": "531",
        "-HonorMax": "1730",
        "-CoinReward": "2000",
        "-DiamondReward": "100",
        "-CardReward": "2#2#2"
      },
      {
        "-ID": "3",
        "-Name": "中士",
        "-HonorMin": "1731",
        "-HonorMax": "3530",
        "-CoinReward": "3000",
        "-DiamondReward": "150",
        "-CardReward": "102#2#1"
      },
      {
        "-ID": "4",
        "-Name": "高阶军士",
        "-HonorMin": "3531",
        "-HonorMax": "6530",
        "-CoinReward": "4000",
        "-DiamondReward": "200",
        "-CardReward": "3#3#2"
      },
      {
        "-ID": "5",
        "-Name": "士官长",
        "-HonorMin": "6531",
        "-HonorMax": "10730",
        "-CoinReward": "5000",
        "-DiamondReward": "250",
        "-CardReward": "4#3#2"
      },
      {
        "-ID": "6",
        "-Name": "石头守卫",
        "-HonorMin": "10731",
        "-HonorMax": "16730",
        "-CoinReward": "6000",
        "-DiamondReward": "300",
        "-CardReward": "5#3#2"
      },
      {
        "-ID": "7",
        "-Name": "血卫士",
        "-HonorMin": "16731",
        "-HonorMax": "33530",
        "-CoinReward": "7000",
        "-DiamondReward": "350",
        "-CardReward": "8#3#2"
      },
      {
        "-ID": "8",
        "-Name": "皇家卫士",
        "-HonorMin": "33531",
        "-HonorMax": "50330",
        "-CoinReward": "8000",
        "-DiamondReward": "400",
        "-CardReward": "101#3#1"
      },
      {
        "-ID": "9",
        "-Name": "百夫长",
        "-HonorMin": "50331",
        "-HonorMax": "67130",
        "-CoinReward": "9000",
        "-DiamondReward": "450",
        "-CardReward": "7#4#1"
      },
      {
        "-ID": "10",
        "-Name": "勇士",
        "-HonorMin": "67131",
        "-HonorMax": "100730",
        "-CoinReward": "10000",
        "-DiamondReward": "500",
        "-CardReward": "6#4#1"
      },
      {
        "-ID": "11",
        "-Name": "中将",
        "-HonorMin": "100731",
        "-HonorMax": "134330",
        "-CoinReward": "11000",
        "-DiamondReward": "550",
        "-CardReward": "9#4#1"
      },
      {
        "-ID": "12",
        "-Name": "将军",
        "-HonorMin": "134331",
        "-HonorMax": "167930",
        "-CoinReward": "12000",
        "-DiamondReward": "600",
        "-CardReward": "10#4#1"
      },
      {
        "-ID": "13",
        "-Name": "督军",
        "-HonorMin": "167931",
        "-HonorMax": "201530",
        "-CoinReward": "13000",
        "-DiamondReward": "650",
        "-CardReward": "103#4#1"
      },
      {
        "-ID": "14",
        "-Name": "高阶督军",
        "-HonorMin": "201531",
        "-HonorMax": "235130",
        "-CoinReward": "14000",
        "-DiamondReward": "700",
        "-CardReward": "104#4#1"
      }
    ]
  }
}


GRADE = _GRADE['Grade']['table']
for v in GRADE:
    v['-HonorMin'] = int(v['-HonorMin'])
    v['-HonorMax'] = int(v['-HonorMax'])
    v['-CoinReward'] = int(v['-CoinReward'])
    v['-DiamondReward'] = int(v['-DiamondReward'])
    # origin_str = v['-CardReward']
    # v['-CardReward'] = origin_str.split('#')

def grade_index_by_honour(honour):
    for k, v in enumerate(GRADE):
        if v['-HonorMin'] <= honour <= v['-HonorMax']:
            return k
    return len(GRADE)
