import random
from typing import List, Dict, Union

MAX_ITEMS = 100

def generate_random_list(length: int) -> List[int]:
    return [random.randint(1, 100) for _ in range(length)]

def process_data(data: List[int]) -> Dict[str, Union[int, float]]:
    result = {}
    result['sum'] = sum(data)
    result['average'] = sum(data) / len(data) if data else 0
    result['max'] = max(data) if data else None
    result['min'] = min(data) if data else None
    return result

class DataAnalyzer:
    def __init__(self, data: List[int]):
        self.data = data
        self.processed_data = None

    def analyze(self):
        self.processed_data = process_data(self.data)

    def get_summary(self) -> str:
        if not self.processed_data:
            return "Data not analyzed yet."
        return f"Sum: {self.processed_data['sum']}, Average: {self.processed_data['average']:.2f}"

    def is_valid(self) -> bool:
        return len(self.data) > 0 and len(self.data) <= MAX_ITEMS

if __name__ == "__main__":
    random_data = generate_random_list(50)
    analyzer = DataAnalyzer(random_data)
    analyzer.analyze()
    print(analyzer.get_summary())
    print(f"Is valid: {analyzer.is_valid()}")