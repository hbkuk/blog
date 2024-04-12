# 쿠폰 발급 시 동시성 제어를 위해 고려했던 4가지 방법

쿠폰 `Entity`에서 **잔여 발급 횟수를 관리**하고 있었습니다.

쿠폰 발급과 관련된 비즈니스 로직을 구현하면서, 동시성 문제에 대해서 궁금해지기 시작했었습니다.

![동시다발적으로 쿠폰 발급 요청](https://github.com/hbkuk/shop/assets/109803585/7546b461-bea0-4e6d-ab99-9ccd91de2a1e)

> 실제 운영환경에서 **여러 Thread가 동시 다발적으로 쿠폰을 발급하기 위해서 데이터베이스에 접근할텐데, 고려해야할 문제는 없을까?**

위와 같은 궁금증에 대해서 해당 프로젝트에서는 **동시성 문제를 어떤 방법으로 해결하려고 했는지?** 이야기 해보려고 합니다.

---

## 단일 `Thread`에서 쿠폰을 발급하는 상황

![단일 Thread에서 쿠폰 발급](https://github.com/hbkuk/shop/assets/109803585/e3afca6e-0569-4beb-8301-5fd508eea9dc)

단일 `Thread`에서 동시성 문제를 고려할 필요가 없지만,  
이후에 나올 내용과 연관되어 있기 떄문에 간단하게 쿠폰을 발급하는 상황을 살펴보겠습니다.

1) 트랜잭션 시작
2) 쿠폰을 발급하기 전, 잔여 쿠폰 개수 조회 → 10개
3) 쿠폰 발급
4) 발급한 쿠폰의 개수만큼 차감
5) 트랜잭션 커밋

위 상황에서 주의깊게 살펴봐야 내용은 **트랜잭션 Commit 된 후 발급 가능한 쿠폰의 개수가 9개로 변경되는 것**입니다.

참고로, 아래 코드는 프로젝트에서 사용했던 코드입니다.

```
@Transactional
public CouponIssueResponse issueCoupon(CouponIssueRequest request, LoginUser loginAdmin) {
    verifyAdminByEmail(loginAdmin);
    verifyMemberByIds(request.getMemberIds());

    Coupon coupon = couponRepository.findByCouponId(request.getCouponId());
    List<IssuedCoupon> issuedCoupons = toIssuedCoupons(request, coupon);
    coupon.issueCoupons(issuedCoupons);

    return CouponIssueResponse.of(issuedCoupons);
}
```

## 다중 `Thread`에서 쿠폰을 발급하는 상황

![다중 Thread에서 쿠폰 발급](https://github.com/hbkuk/shop/assets/109803585/26fbb401-4ab2-4a6c-893c-f831f891a966)

이제 동시성 문제가 발생할 수 있는, **다중 `Thread`가 쿠폰을 발급하는 상황**을 살펴보겠습니다.   

`tx1`은 Transaction 1을 의미하고, `tx2`는 Transaction 2을 의미합니다.  

`tx1`과 `tx2`이 쿠폰을 발급하는 과정은 앞서 언급되었던 단일 `Thread`에서 쿠폰을 발급한 것과 동일합니다.  
다만, `tx1`이 차감한 개수를 데이터베이스에 반영(트랜잭션 커밋)하기 전, `tx2`가 발급 가능한 쿠폰의 개수를 조회했습니다.


위 그림을 보면 알 수 있듯이... 어떠한 상황이 발생할 수 있을까요?

`tx1`은 쿠폰의 개수를 **10개에서 9개로 차감한 개수**(-1)를 데이터베이스에 반영하고, `tx2`도 마찬가지로 쿠폰의 개수를 **10개에서 9개로 차감한 개수**(-1)를 데이터베이스에 반영했습니다.  
결과적으로, **실제로 발급된 쿠폰의 개수는 2개**가 됩니다.

100개, 1000개의 `Thread`가 동시에 요청했다면 어떤 상황이 발생할까요?  
~~(정말 상상만 해도 끔찍하다.)~~

저는 앞으로 이러한 동시성 문제가 가까운 미래에 충분히 발생할 수 있을 것이라고 생각하면서, 동시성 문제에 대해서 진중하게 접근해보고자 했습니다.  

---

## 동시성 문제를 해결할 수 있는 4가지 방법

1. `sychronized` 키워드 추가
2. 낙관적 락 (Optimistic Lock) 사용
3. 비관적 락 (Pessimistic Lock) 사용
4. 외부 저장소 활용(Redis 등)

### `sychronized` 키워드 추가

![synchronized 키워드 추가](https://github.com/hbkuk/shop/assets/109803585/5ebab66d-80b2-4f21-b60a-8e75550a5895)

하나의 `Thread`만 접근 가능하도록 메서드에 `sychronized` 키워드를 추가했습니다.

잠깐 `sychronized` 원리를 간단하게 알아볼까요?  
> 인스턴스마다 하나의 `monitor`를 가지고 있고, `Thread`는 `monitor`를 잠금 혹은 해제할 수 있다.  
> 오직 하나의 `Thread`만이 `monitor`에 대해 잠금을 획득할 수 있고, 잠금을 가지려 하는 다른 `Thread`들은 잠금이 해제할 때까지 차단된다.

위에서 언급되었듯이, 하나의 `Thread`만 메서드를 실행시킬 수 있습니다.  
하지만, 현재 상황에서 2가지 정도의 문제를 해결하는 것이 좋을 것 같습니다.      

1. `@Transaction` 어노테이션으로 인해 데이터베이스에 반영(트랜잭션 커밋)하기 전, 다른 `Thread`에서 잠금을 획득 후, 쿠폰을 발급할 수 있다.
2. 향후 분산 서버 환경(**scale-out**으로 인한)에서 동시성 문제를 여전히 발생한다.

#### 데이터베이스에 반영(트랜잭션 커밋)하기 전, 다른 `Thread`에서 잠금을 획득

우선, 첫번째 문제에 대해서 그림으로 표현해보자면 다음과 같습니다.

![synchronized 키워드에서 발생하는 동시성 문제](https://github.com/hbkuk/shop/assets/109803585/4a3a476e-c127-4d02-86f9-ea146bd783ca)

앞서, 트랜잭션이 시작되고 `commit` 되는 시점에 변경 사항이 데이터베이스에 반영된다고 했었습니다.  

`sychronized` 키워드를 통해 하나의 `Thread`만 실행되도록 보장했으나,   
**다른 `Thread`에서 트랜잭션 `commit` 전 잠금을 획득할 수 있기 때문에** 여전히 동시성 문제가 남아있습니다.  

#### 분산 서버에서 동시 실행

두번째 문제에 대해서는, 간략하게 그림으로 표현해보자면 다음과 같습니다.

![synchronized 키워드에서 발생하는 동시성 문제 2](https://github.com/hbkuk/shop/assets/109803585/b13e43a8-cd46-4b98-a588-0d05771ead9b)

각 분산 서버의 `Thread` 1이 동시에 실행된다면, 이전과 같은 동시성 문제가 발생합니다.  
그렇다면, 현재 상황에서는 `synchronized` 키워드로 해결할 수는 없는 것으로 확인할 수 있습니다.  

### 낙관적 락 (Optimistic Lock) 사용

> 데이터를 읽을 때는 잠금을 걸지 않고, 데이터를 수정할 때에는 해당 엔티티의 버전을 비교하여 충돌을 감지한다.  
> 즉, 애플리케이션 레이어에서 지원하는 `Lock`이다.

이를 구현하기 위해서는, JPA에서 제공하는 `@Version` 어노테이션을 사용할 수 있습니다.  
따라서, 아래와 같이 Coupon `Entity`에 버전을 관리할 수 있는 필드를 추가했습니다.  

```
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Coupon {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    private String description;

    private LocalDateTime createdAt;

    @Enumerated(EnumType.STRING)
    private CouponStatus couponStatus;
  
    // ...
  
    @Version
    private Integer version;
  
}
```

데이터를 수정하기 전에 엔티티의 버전을 확인합니다.   
또한, `Coupon` 엔티티가 수정될 때마다 해당 필드의 값이 증가하게 됩니다.  

```
UPDATE COUPON
SET
  remaining_issue_count = ?,
  version = ? # 버전 + 1 증가
WHERE
  id = ?,
  and version = ? # 버전 비교
```

이를, 그림으로 표현해보자면 다음과 같습니다.

![낙관적 락](https://github.com/hbkuk/shop/assets/109803585/b81b59be-522c-4494-aef1-e7bbb2afb398)

위에서 표현된 것과 같이, `tx1`이 엔티티를 수정한 후 버전이 증가한 경우에 `tx2`가 해당 엔티티를 수정하려고 한다면, JPA는 버전이 변경되었음을 감지하고 예외를 던집니다.  
따라서, 애플리케이션 레벨에서 이를 처리해줘야 합니다.  
예) 리트라이(Re-try) 메커니즘

그렇다면, 낙관적 `Lock`은 어느 상황에서 사용하는 것이 좋은 방법일까요?  
아래와 같이 정리해볼 수 있을 것 같습니다.  

1. 읽기(Read)가 많고, 쓰기(Write)가 적은 상황
2. 트랜잭션 충돌이 상대적으로 적을 것으로 예상하는 상황

추가적으로 JPA에서는 `LockModeType`을 제공하고 있으므로 궁금하신 분들은 해당 키워드에 대해서 학습해보는 것을 추천합니다.

![낙관적 락 LockModeType](https://github.com/hbkuk/shop/assets/109803585/a3e5f26c-8036-433e-a0dd-a3ca70f9f2ad)

### 비관적 락 (Pessimistic Lock) 사용

> 데이터를 읽을 때부터 잠금을 걸고, 해당 데이터를 수정할 때까지 잠금을 유지한다.
> 즉, 데이터베이스에서 지원하는 Lock이다.

주로 `SELECT ... FOR UPDATE` 문을 사용하여 구현됩니다.  
해당 쿼리는 특정 레코드를 읽고 수정하는 동안 다른 트랜잭션들이 해당 레코드를 읽거나 수정하는 것(배타 락으로 잠금)을 방지합니다.  

그림으로 표현해보자면, 다음과 같습니다.  

![비관적 락](https://github.com/hbkuk/shop/assets/109803585/0ef93abd-9485-4321-94dc-dc93ae8bb06f)

`tx1`과 `tx2`에서 트랜잭션이 시작되고, `tx1`이 먼저 `SELECT ... FOR UPDATE` 문을 통해 `Lock`을 획득했습니다.  
해당 **테이블 혹은 레코드에 대한 읽기와 쓰기에 대한 잠금이 설정**됩니다.    
따라서, `tx2`는 `tx1`이 커밋된 후, 잠금이 해제되는 시점까지 대기하게 됩니다.

위에서 **'테이블 혹은 레코드'** 라고 표현한 것은,   
> `SELECT ... FOR UPDATE` 문에서 `Lock`의 범위는 **주로 인덱스와 WHERE 절에 지정된 조건에 의해 결정됩니다.**  

조금 더 자세히 알고싶으시다면, [InnoDB의 Lock 처리 방식](https://miintto.github.io/docs/mysql-select-for-update) 참고하시면 좋을 것 같습니다.  


비관적 락이 동작하는 상황을, 로그로 확인해본다면 어떨까요?  

```
Thread 1: 트랜잭션 시작
Thread 1: findByCouponIdWithLock 메서드 호출 -> 쿠폰 엔티티에 대한 쓰기 잠금 획득
Thread 2: 트랜잭션 시작
Thread 2: findByCouponIdWithLock 메서드 호출 -> 쿠폰 엔티티에 대한 쓰기 잠금 대기 중...
...
Thread 1: findByCouponIdWithLock 메서드 종료 -> 쿠폰 엔티티 조회 완료
Thread 1: 발급 쿠폰 생성 및 업데이트 시작
Thread 1: 발급 쿠폰 생성 및 업데이트 완료
Thread 1: 트랜잭션 커밋 -> 쓰기 잠금 해제
...
Thread 2: findByCouponIdWithLock 메서드 호출 -> 쿠폰 엔티티에 대한 쓰기 잠금 획득
Thread 2: 쿠폰 엔티티 조회 완료
Thread 2: 발급 쿠폰 생성 및 업데이트 시작
Thread 2: 발급 쿠폰 생성 및 업데이트 완료
Thread 2: 트랜잭션 커밋 -> 쓰기 잠금 해제
```

비관적 락을 구현하는 방법은 JPA에서 제공하는 `@Lock` 어노테이션을 사용하면 됩니다.  

```
public interface CouponRepository extends JpaRepository<Coupon, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select coupon from Coupon coupon where coupon.id = :couponId")
    Coupon findByCouponIdWithLock(@Param("couponId") Long couponId);
}
```

`Lock` 모드는 3가지를 제공합니다.  

1. `PESSIMISTIC_WRITE`: 엔티티에 대한 쓰기 잠금을 설정
2. `PESSIMISTIC_READ`: 엔티티에 대한 읽기 잠금을 설정
3. `PESSIMISTIC_FORCE_INCREMENT`: Version 정보 활용

그렇다면, 비낙관적 `Lock`은 어느 상황에서 사용하는 것이 좋을까요?   
아래와 같이 정리해볼 수 있을 것 같습니다.  

1. 쓰기(Write) 작업이 빈번하게 발생하는 상황
2. 트랜잭션 충돌이 상대적으로 많을 것으로 예상하는 상황

동시성 제어를 위해 낙관적 락뿐만 아니라, 비관적 락 또한 좋은 방법인 것은 확실한 것 같습니다.  

## 분산 DB 환경에서 생각해보기

앞에서, 낙관적 락과 비관적 락을 살펴보았습니다.

서비스를 운영하다보면, 규모가 점점 커져서 분산 DB 환경이 될것으로 예상하는데, 이러한 상황에서 여전히 좋은 솔루션일까요?  
아래 그림으로 확인해보겠습니다.  

![분산 DB](https://github.com/hbkuk/shop/assets/109803585/3ea82b4f-2096-47be-a1ee-cd8bf455f8c1)

일반적인 분산 데이터베이스 구조로는 `Master-slave` 구조입니다.  

> Master-slave 구조란?  
> 마스터 서버는 데이터의 쓰기 작업을 담당하고, 이 변경 내용을 슬레이브 서버들에 복제(replicate)하여 데이터의 일관성을 유지한다.  
> 읽기 작업은 슬레이브 서버들이 처리하기 때문에 읽기 부하를 분산시키고 성능을 향상시킬 수 있다.

이러한 구조에서 Lock을 관리하고 동기화한다는 것은 상상만 해도 어려울 것 같다는 듭니다.  
이러한 상황에서 더 좋은 솔루션이 무엇일까요?

`Redis`와 같은 외부 저장소를 활용하는 방법일 것으로 예상됩니다.  
이 부분은 기회가 된다면, 나중에 포스팅 해보겠습니다.

## 별첨) 트랜잭션 격리레벨로 동시성 문제를 해결할 순 없었을까?  

트랜잭션의 격리레벨로 해결할 수 없었을까요?

![트랜잭션으로 해결해보기](https://github.com/hbkuk/shop/assets/109803585/4a519e4c-fb5c-4700-8e28-7f3d1f4963b5)

여러 `Thread`가 쿠폰을 발급하는 상황에서는 가장 첫번째 트랜잭션만 성공하고 나머지 트랜잭션은 아래와 같이 롤백됩니다.  

![데드락 발생 로그](https://github.com/hbkuk/shop/assets/109803585/7b99311a-318e-452c-9d23-677f41a1c09a)



https://hudi.blog/jpa-concurrency-control-optimistic-lock-and-pessimistic-lock/

참고

- [풀필먼트 입고 서비스팀에서 분산락을 사용하는 방법 - Spring Redisson](https://helloworld.kurly.com/blog/distributed-redisson-lock/)
- [Lock을 사용할 때 트랜잭션 범위를 고려하자](https://medium.com/@dori_dori/lock%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%A0-%EB%95%8C-%ED%8A%B8%EB%9E%9C%EC%9E%AD%EC%85%98-%EB%B2%94%EC%9C%84%EB%A5%BC-%EA%B3%A0%EB%A0%A4%ED%95%98%EC%9E%90-8f60f4da5248)
- [InnoDB의 Lock 처리 방식](https://miintto.github.io/docs/mysql-select-for-update)
