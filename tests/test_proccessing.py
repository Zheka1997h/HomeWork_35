import pytest
from src.proccessing import List, Dict

# Предполагаем, что функции filter_by_state и sort_by_date уже определены

def filter_by_state(transactions: List[Dict], state: str = 'EXECUTED') -> List[Dict]:
    return [transaction for transaction in transactions if transaction.get('state') == state]

def sort_by_date(transactions: List[Dict], descending: bool = True) -> List[Dict]:
    return sorted(transactions, key=lambda x: x['date'], reverse=descending)

# Фикстура для подготовки данных транзакций
@pytest.fixture
def transactions():
    return [
        {'id': 1, 'date': '2023-10-01', 'state': 'EXECUTED'},
        {'id': 2, 'date': '2023-09-30', 'state': 'CANCELED'},
        {'id': 3, 'date': '2023-10-02', 'state': 'EXECUTED'},
        {'id': 4, 'date': '2023-09-29', 'state': 'PENDING'}
    ]

# Параметризованные тесты для filter_by_state
@pytest.mark.parametrize("state, expected_ids", [
    ('EXECUTED', [1, 3]),
    ('CANCELED', [2]),
    ('PENDING', [4]),
    ('NOT_EXISTING', [])
])
def test_filter_by_state(transactions, state, expected_ids):
    filtered = filter_by_state(transactions, state)
    assert len(filtered) == len(expected_ids)
    assert [t['id'] for t in filtered] == expected_ids

# Параметризованные тесты для sort_by_date
@pytest.mark.parametrize("descending, expected_order", [
    (True, [3, 1, 2, 4]),  # По убыванию
    (False, [4, 2, 1, 3])  # По возрастанию
])
def test_sort_by_date(transactions, descending, expected_order):
    sorted_transactions = sort_by_date(transactions, descending)
    assert [t['id'] for t in sorted_transactions] == expected_order


