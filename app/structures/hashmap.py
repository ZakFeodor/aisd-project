import pandas as pd

class MyHashMap:
    MAX_LOAD_FACTOR = 0.75

    def __init__(self, capacity=8):
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(capacity)]

    def _index(self, key):
        return hash(key) % self.capacity

    def load_factor(self):
        self.load_factor = self.size / self.capacity
        return self.load_factor

    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)

    def put(self, key, value):
        index_of_key = MyHashMap.contains(self, key)
        if index_of_key:
          new_index = MyHashMap._index(self, key)
          self.buckets[new_index][index_of_key-1] = (key, value)
        else:
          if (self.size + 1) / self.capacity > MyHashMap.MAX_LOAD_FACTOR:
            MyHashMap._resize(self)
          new_index = MyHashMap._index(self, key)
          self.buckets[new_index].append((key, value))
          self.size += 1
    def get(self, key):
        index = MyHashMap._index(self, key)
        if MyHashMap.contains(self, key):
          for a, b in self.buckets[index]:
              if a == key:
                return b
        else:
          return None

    def contains(self, key):
        index = MyHashMap._index(self, key)
        for i in range(len(self.buckets[index])):
          if key == self.buckets[index][i][0]:
            return i+1
        return False
    def remove(self, key):
        index = MyHashMap._index(self, key)
        if MyHashMap.contains(self, key):
          for i in range(len(self.buckets[index])):
            if self.buckets[index][i][0] == key:
              self.buckets[index].pop(i)
              self.size -= 1
              return True
        else:
          return False
    def __len__(self):
        return self.size

def build_hash_index(file_path):
    df = pd.read_csv(file_path)
    index = MyHashMap()

    for row_id, key in enumerate(df['Transaction_ID']):
        index.put(key, row_id)

    return index

def get_row(file_path, transaction_id, hashmap):
    df = pd.read_csv(file_path)
    row_number  = hashmap.get(transaction_id)
    if row_number is None:
        return None
    return df.iloc[row_number].to_dict()

if __name__ == '__main__':
    from pathlib import Path
    base = Path(__file__).resolve().parent.parent.parent
    row = get_row(str(base / "uploads" / "admin" / "Retail_Transactions_Dataset.csv"), int(1000000028))
    print(row)

