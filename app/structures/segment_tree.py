class SegmentTree:
    def __init__(self, a):
        self.n = len(a)
        self.array = a
        self.tree = [0] * (4 * self.n)
        self._build(1, 0, self.n-1)

    def _build(self, v, tl, tr):
        if tl == tr:
          self.tree[v] = self.array[tl]
          return self.tree[v]

        self.tree[v] = self._build(2*v, tl, (tl+tr)//2) + self._build(2*v+1, (tl+tr)//2+1, tr)

        return self.tree[v]


    def query(self, l, r):
        if l >= 0 and r<self.n:
          return self._query(1, 0, self.n-1, l, r)
        else:
          raise ValueError('Ошибка границ передаваемых значений')

    def _query(self, v, tl, tr, l, r):
        if tl < l <= tr or tl <= r < tr:
            return self._query(2 * v, tl, (tl + tr) // 2, l, r) + self._query(2 * v + 1, (tl + tr) // 2 + 1, tr, l, r)
        elif l <= tl and r >= tr:
            return self.tree[v]
        else:
            return 0

    def update(self, pos, value):
        if 0 <= pos < self.n:
          self.array[pos] = value
          self._update(1, 0, self.n-1, pos, value)
        else:
          raise ValueError('Ошибка позиции')

    def _update(self, v, tl, tr, pos, value):
        if tl <= pos <= tr:
          if pos == tr == tl:
            self.tree[v] = value
          else:
            self.tree[v] = self._update(2*v, tl, (tl+tr)//2, pos, value) + self._update(2*v+1, (tl+tr)//2+1, tr, pos, value)
        return self.tree[v]

