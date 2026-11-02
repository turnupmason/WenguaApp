"""Audit requested V27 clocks: independent calendar, nine palaces and text."""
import json
import sys
from pathlib import Path
from src.wengua.health_discomfort_v19_parity import compare_jsonl
from src.wengua.health_lifecycle_v391 import source_full12
from tests.test_ios_five_random_live_casts import generated_case


def report(path):
    compare_jsonl(path)
    cases = [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]
    requested = json.loads(Path('data/evaluation/health_discomfort/v27_brother_wife_random_20261102.json').read_text())['cases']
    assert len(cases) == len(requested) == 2
    result = ['## V27 哥哥、妻子随机病位实测', '',
              '普通身体不适；未提供年命。仅为软件技术测试，非临床诊断或盲测。', '']
    for case, request in zip(cases, requested):
        board, reading = case['chart'], case['reading']
        assert reading['relationship'] == request['relationship']
        assert board['iso'] == request['iso'] and case['injuryContext'] == 'none'
        expected, palaces, extra = generated_case(board['iso'], source_full12())
        for key in ('pillars', 'bureau', 'xunShou', 'valueStar', 'valueDoor', 'voidBranches'):
            assert board[key] == expected[key], key
        for native in board['palaces']:
            original = palaces[native['id']]
            for key in ('earthStem', 'door', 'deity', 'heavenStars', 'voidBranches'):
                assert native.get(key) == original.get(key), (native['id'], key)
        result += [f"### {reading['relationship']} · {board['iso']}", '',
                   '四柱：' + ' / '.join(board['pillars'][k] for k in ('year','month','day','hour')), '',
                   'PASS：独立历法、九宫与 Python/Swift 完整中文逐字一致。', '']
        for section in reading['sections']:
            result += [section['title'] + '：' + section['text'], '']
    return '\n'.join(result)

if __name__ == '__main__':
    print(report(sys.argv[1]))
