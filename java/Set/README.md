<div class="markdown-body">  

# Set of Collections Framework  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/95356c0c-8efe-4cef-a411-822a0de74d3d" alt="text" width="number" />
</p>  

`Set`은 **집합**이라는 의미를 가진다.  

여기서 말하는 집합은 집합 안에 있는 요소들은 <u>**순서**</u>도 없고, <u>**중복**</u>을 허용하지 않는 것을 의미한다.  

<br>

Java 진영에서의 이러한 의미를 가진 클래스를 제공한다.  

Collections Framework 중 하나인 `Set`이라는 인터페이스를 제공하며, 이를 구현한 3가지의 클래스를 다음과 같이 제공한다.  

- Hash 알고리즘을 이용한 `HashSet`
- 이진 탐색 트리를 사용하여 오름차순 정렬까지 해주는 `TreeSet`
- Set에 순서를 부여해주는 `LinkedHashSet`  

<br>  

## 언제 Set을 사용하면 좋을까?  

순서가 상관없고 중복을 허용하지 않는 상황이라면, 다음과 같은 상황이 될 수 있겠다.  
- 집합 관련 문제로 풀어낼 수 있는 상황일 때
- 중복 처리를 고려해야할 때  

<br>  

## 교집합(intersect), 차집합(difference), 합집합(union) 구현  

#### 해당 내용은 [생활코딩의 배열과 컬렉션즈 프레임워크](https://opentutorials.org/module/516/6446)를 참고해서 작성했습니다.  

다음과 같이 서로 다른 3개의 집합 `A`, `B`, `C`가 있다고 가정해보자.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/c87ee335-3823-4317-97f6-741e22f74618" alt="text" width="number" />
</p>  

Set 클래스에서 제공하는 메서드를 확인 해보고, 이를 이용해서 집합연산을 진행해보자.  

- `containsAll` : 두 Collection이 **동일한 요소를 포함하는지 여부**를 확인하는데 사용
    - 인자로 전달된 Collection의 모든 요소가 집합에 있으면 `True` 반환
- `addAll()`: 인자로 전달된 Collection 객체의 **모든 요소를 Set에 추가**
- `retainAll()`: 두 Collection의 **공통적인 요소는 남기고 그 외의 요소들은 삭제**  
- `removeAll`: 인자로 전달된 Collection 객체의 요소가 존재한다면 **그 요소들을 삭제**  

<br>    

### containsAll() 메서드를 사용해서 부분집합인지 확인  

```
@Nested
@DisplayName("부분집합")
class subSet {
    @Test
    @DisplayName("B는 A의 부분집합이 아니다.")
    void not_subset_AB() {
        assertThat(A.containsAll(B)).isFalse();
    }
    @Test
    @DisplayName("C는 A의 부분집합이다.")
    void subset_AC() {
        assertThat(A.containsAll(C)).isTrue();
    }
    @Test
    @DisplayName("C는 B의 부분집합이 아니다.")
    void not_subset_BC() {
        assertThat(B.containsAll(C)).isFalse();
    }
}
```  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/ebd4e1c4-ae37-4bee-af89-682ae4f0b36b" alt="text" width="number" />
</p>  

위 내용을 그림으로 정리하면 다음과 같다.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/bf4f9d13-ab0e-47b8-bc19-ade003f7b9b1" alt="text" width="number" />
</p>  

<br>  

### addAll() 메서드를 사용해서 합집합 구현  

```
@Nested
@DisplayName("A-B 합집합")
class union {
    @Test
    @DisplayName("1 ~ 5의 숫자가 포함되어있다.")
    void union_AB() {
        // then
        A.addAll(B);

        // when
        assertThat(A).contains(1)
                    .contains(2)
                    .contains(3)
                    .contains(4)
                    .contains(5)
                    .doesNotContain(6);
    }
}
```  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/bcb9d169-0396-4bec-8a51-aecc1d45ff6d" alt="text" width="number" />
</p>  

<br>

### retainAll() 메서드를 사용해서 교집합 구현  

```
@Nested
@DisplayName("A-B 교집합")
class intersect {
    @Test
    @DisplayName("3 만 포함되어 있다.")
    void intersect_AB() {
        // then
        A.retainAll(B);

        // when
        assertThat(A).doesNotContain(1)
                .doesNotContain(2)
                .contains(3)
                .doesNotContain(4)
                .doesNotContain(5)
                .doesNotContain(6);
    }
}
```  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/4f843b99-3206-440c-b931-73da61e36ba2" alt="text" width="number" />
</p>  

<br>

### removeAll() 메서드를 사용해서 차집합 구현  

```
@Nested
@DisplayName("A-B 차집합(A 기준 - B)")
class difference {
    @Test
    @DisplayName("1과 2만 포함되어 있다.")
    void difference_AB() {
        // then
        A.removeAll(B);

        // when
        assertThat(A).contains(1)
                .contains(2)
                .doesNotContain(3)
                .doesNotContain(4)
                .doesNotContain(5)
                .doesNotContain(6);

    }

}
```  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/c1395d43-aff3-41e4-a46e-0ac60f0afea5" alt="text" width="number" />
</p>  

</div>