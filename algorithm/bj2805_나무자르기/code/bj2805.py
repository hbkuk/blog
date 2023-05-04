"""
1. 아이디어
- 완전 탐색할 경우 시간복잡도는 O(N*N), 여기서 N은 10^6 이므로 ==> 시간초과!

- while( st < ed )
    - mid를 기준으로 짤랐을 때
        - 자른 나무의 총길이 > 상근이가 가져가야 하는 나무의 길이
            - mid = 시작점
        - 자른 나무의 총길이 < 상근이가 가져가야 하는 나무의 길이
            - mid - 1 = 끝점

2. 시간복잡도
- 정렬 O(N*lgN)
- 이진탐색 O(N*lgN)
- 결과적으로 O((N+N(lgN)) .. (2^10)^2 = (10^3)^2 ==> 4백만 < 2억개 !! => 이진탐색 가능

3. 자료구조
- 나무 리스트 int[]
"""

import sys
input = sys.stdin.readline

N, M = map(int, input().split())
trees = list(map(int, input().split()))

st = 0
ed = max(trees)

while(st < ed):
    mid = (st + ed) // 2 + 1

    sum = 0
    for tree in trees:
        if tree > mid:
            sum += (tree - mid)
    
    if sum >= M:
        st = mid
    else:
        ed = mid - 1

print( st )
