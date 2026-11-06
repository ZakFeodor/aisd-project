def leonardo(k):
    if k < 2:
        return 1
    a, b = 1, 1
    for _ in range(2, k + 1):
        a, b = b, a + b + 1
    return b


def smooth_sort(unsorted):
    def sift(start, end):
        i = start
        j = 0
        k = 0
        while k < end - start + 1:
            if k & 0xAAAAAAAA:
                j = j + i
                i = i >> 1
            else:
                i = i + j
                j = j >> 1
            k = k + 1
        while i > 0:
            j = j >> 1
            k = i + j
            while k < end:
                if unsorted[k] < unsorted[k - i]:
                    break
                unsorted[k], unsorted[k - i] = unsorted[k - i], unsorted[k]
                k = k + i
            i = j
            j = k - i

    n = len(unsorted)
    if n <= 1:
        return unsorted

    p = n - 1
    q = p
    r = 0
    while p > 0:
        if (r & 0x03) == 0:
            sift(r, q)
        if leonardo(r) == p:
            r = r + 1
        else:
            r = r - 1
            q = q - leonardo(r)
            sift(r, q)
            q = r - 1
            r = r + 1
        unsorted[0], unsorted[p] = unsorted[p], unsorted[0]
        p = p - 1

    for i in range(n - 1):
        j = i + 1
        while j > 0 and unsorted[j] < unsorted[j - 1]:
            unsorted[j], unsorted[j - 1] = unsorted[j - 1], unsorted[j]
            j = j - 1

    return unsorted

if __name__ == '__main__':
    print(smooth_sort([8, 2, 4, 4, 5, 6, 7, 8, 9, 3, 11, 55, 13, 6, 15]))