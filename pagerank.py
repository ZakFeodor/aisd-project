edges = [
    ("A", "B"),
    ("A", "D"),
    ("B", "C"),
    ("C", "A"),
    ("C", "D"),
    ("D", "E"),
    ("E", "C"),
    ("E", "F"),
    ("F", "C"),
]

def pagerank(edges=edges, d=0.85, eps=1e-6, max_iter=100):
    nodes = set()
    out_deg = {}
    for u, v in edges:
        nodes.add(u)
        nodes.add(v)
        out_deg[u] = out_deg.get(u, 0) + 1
    for n in nodes:
        out_deg.setdefault(n, 0)

    N = len(nodes)
    if N == 0:
        return {}

    incoming = {n: [] for n in nodes}
    for u, v in edges:
        incoming[v].append(u)

    pr = {n: 1.0 / N for n in nodes}

    for _ in range(max_iter):
        dangling_sum = sum(pr[n] for n in nodes if out_deg[n] == 0)
        new_pr = {}
        for n in nodes:
            s = sum(pr[u] / out_deg[u] for u in incoming[n] if out_deg[u] > 0)
            new_pr[n] = (1 - d) / N + d * (s + dangling_sum / N)
        diff = sum(abs(new_pr[n] - pr[n]) for n in nodes)
        pr = new_pr
        if diff < eps:
            break

    return pr


if __name__ == "__main__":

    ranks = pagerank(edges)
    print(ranks)
    print("Результаты PageRank:")
    for node, rank in sorted(ranks.items(), key=lambda x: -x[1]):
        print(f"{node}: {rank:.4f}")