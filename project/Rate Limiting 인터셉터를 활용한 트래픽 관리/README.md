<div class=markdown-body>

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.  

<br>  

## Rate Limit에 대해서 고민을 하게된 계기

현재 컨테이너 기반 PaaS 클라우드 서비스를 이용해서 배포 후 운영 중, 잠시 다음과 같은 생각을 하게되었는데요.

**추후 실제 서비스를 시작하게 된다면? ... 혹은 사용자가 점차 늘어난다면? 어떠한 플랜을 구독할까?.. 또 어떠한 플랜들이 있을까?**

![Cloud Type Plan](https://github.com/hbkuk/now-back/assets/109803585/1550984a-7bee-4b9f-bc29-b4118e2991f8)
출처: *https://www.cloudtype.io/pricing*

**현재 사용 중인 플랜은 디벨로퍼**로,  
매달 **허용하는 트래픽을 10GB로 제한**하고있는데, **현재 서비스에서 대략적으로 발생되는 트래픽량이 어느정도인지 가늠**해보고자 했습니다.  

메인 페이지 기준으로 디버깅을 해보았습니다.  

<br>

### 초기 로딩 시  

현재 **프로젝트 구조가 SPA(Single Page Application)** 이다 보니  
초기 로딩 시에 **대부분의 리소스를 모두 다운로드 해야하므로, 트래픽이 꽤나 무거**웠습니다.

![네트워크 탭](https://github.com/hbkuk/now-back/assets/109803585/5a63e03b-8d77-414f-a602-91b471c80921)

- 이미지(별도 클라우드 스토리지 사용)를 제외한 **전송량 약 1.3 MB**  

<br>

### 페이지 이동 혹은 새로고침 시  

![브라우저캐시사용_새로고침](https://github.com/hbkuk/now-back/assets/109803585/1e1790a1-fb36-4880-bf8a-8261c17a6862)

- 브라우저 캐시를 사용해서 새로고침 시 **전송량 약 14 kB**  

<br>  

**하루 동안의 트래픽을 계산하기 위해서 몇가지 가정**을 해보았습니다.  

- 하루동안 **20명의 사용자가 방문**
- 페이지 이동 혹은 새로고침을 **10회** 

```
- 26 MB (초기 로딩) + 140 KB (페이지 이동 또는 새로고침) = 26.14 MB
```  

<br>

이를 **한달(30일)로 환산**하면

```
- 26.14 MB * 30 = 784.2 MB
```  

<br>

이를 **GB(기가 바이트)로 환산**하면

```
- 784.2 MB / 1024 = 약 0.766 GB
```

**한 달 동안 약 0.766GB의 트래픽이 발생**할 것입니다.  

<br>

이론적으로 계산했을 때, **당분간 현재 플랜으로 유지해도 문제가 없겠구나**라고 결론을 내리게 되었습니다.  

<br>

### 악의적인 사용자에 의해서 트래픽이 급증한다면?  

한 달 동안 약 0.766GB의 트래픽이 발생한다는 것은 **현재 플랜이 해당 트래픽을 처리하는 데에는 문제가 없다는 것을 의미**합니다.  

그러나 과거에도 **악의적인 사용자로부터의 대량 트래픽으로 인해 서버 다운 문제가 있었던 사례를 고려**하면, **Rate Limit 설정이 필요**하다고 판단했습니다.

<br>

### Bucket4j 라이브러리

Bucket4j는 **Java 8 이상과 호환성이 좋은, 스프링과 쉽게 통합**할 수 있는 라이브러리인데요.  

**두 가지 주요 Rate Limiting 알고리즘을 구현**하고 있습니다.
그 중 **토큰 버킷(Token Bucket) 알고리즘을 선택한 이유는 적은 메모리를 사용한다는 이유**가 가장 컸습니다. 

그러나, 적은 메모리를 사용하는 만큼 단점이 있는데요.  
그것은 **분산 환경에서 동시에 들어오는 요청에 대해 Race condition이 발생할 수 있다는 문제**가 있다는 것입니다.  

<br>

이와 같은 내용은 **추후 서버 확장 시 고려**하고자 합니다.

따라서, 현재 사용하고 하는 알고리즘인, **토큰 버킷(Token Bucket) 알고리즘에 대해서 간략하게 정리**를 해보겠습니다.  

![Token Bucket Algorithm](https://github.com/hbkuk/now-back/assets/109803585/f8a02246-2d66-471c-a50a-bcbb27f4a9da)

**Token Bucket Algorithm**
- **Token이 담겨진 Bucket**을 가정하고, **요청을 처리하는 비용으로 Token을 지불**하는 방식으로 처리에 제한을 설정한 Algorithm
- **Bucket에 남겨진 Token이 부족하면 요청은 Reject 처리**
- **Bucket에 Token은 시간을 기반으로 다시 채워지게 설계**
- **일정 수준의 부하 처리도 Bucket에 남은 Token을 기반으로 해서 일정 수준으로 처리 가능**  

<br>  

### Rate Limiting Interceptor 설계  

이제 본격적으로, **Rate Limit 설정을 위해 Interceptor 선언**했는데요.

아래와 같이 **두가지의 책임으로 나누어서 각 객체에게 위임**했습니다.

![인터셉터 설계](https://github.com/hbkuk/now-back/assets/109803585/d42def92-aab0-40f5-99cb-b2843413cdf8) 

- `RateLimitBucketMap`: 주어진 **IP 주소에 대한 Rate Limit 버킷이 존재하는지 확인**하거나, 해당 IP 주소에 대한 **Rate Limit 버킷을 가져오는 역할**
- `RateLimitingBucketProvider`: Rate Limit **버킷을 생성하고 반환하는 역할**  

<br>

#### RateLimitBucketMap  

```
@Component
@RequiredArgsConstructor
public class RateLimitBucketMap {
    private final Map<String, Bucket> bucketConcurrentHashMap = new ConcurrentHashMap<>();

    /**
     * 주어진 IP 주소에 대한 버킷이 존재하면 true 반환, 그렇지 않다면 false 반환
     *
     * @param ipAddress IP 주소
     * @return 버킷이 존재하면 true, 그렇지 않으면 false 반환
     */
    public boolean hasBucket(String ipAddress) {
        return bucketConcurrentHashMap.containsKey(ipAddress);
    }

    /**
     * 주어진 IP 주소에 대한 버킷 반환
     *
     * @param ipAddress IP 주소
     * @return IP 주소에 대한 버킷 객체
     */
    public Bucket getBucket(String ipAddress) {
        return bucketConcurrentHashMap.get(ipAddress);
    }

    /**
     * 주어진 IP 주소에 새로운 버킷 추가
     *
     * @param ipAddress IP 주소
     * @param bucket    추가할 버킷 객체
     */
    public void addBucket(String ipAddress, Bucket bucket) {
        bucketConcurrentHashMap.put(ipAddress, bucket);
    }
}
```  

**`ConcurrentHashMap`을 사용한 이유는, Multi-Thread 환경에서 안전하게 동작**하기 위해서 선택하게 되었는데요.  

예를 들어, `ConcurrentHashMap`을 사용하지 않을 때 **여러 Thread가 Map에 접근할 때 Lock을 획득하려고 시도**하다보니, 다음과 같은 상황이 발생할 수 있습니다.  

- **Lock 경합 (Lock Contention)**: 여러 Thead가 동시에 Map에 접근하려고 할 때 Lock을 얻기 위해 경합 발생
- **성능 저하**: Lock 경합으로 인해 Thead들이 대기하게 되면 처리 속도가 느려짐
- **데드락 가능성**: Thead 간에 서로가 가진 Lock을 해제하지 못하고 무한정 대기하는 상황  

따라서, **여러 Thread가 동시에 Map에 접근할 수 있고, Lock 경합을 최소화하기위해 ConcurrentHashMap을 선택**했습니다.

<br>  

#### RateLimitingBucketProvider  

![Provider 객체](https://github.com/hbkuk/now-back/assets/109803585/2b0e9025-d3f4-47df-bec0-01958181a7bc) 

**필드에 선언된 상수**를 살펴보겠습니다.  

- `MAX_BANDWIDTH`: **최대 처리할 수 있는 요청의 횟수**(혹은 최초 토큰 개수)
- `TOKEN_REFILL_COUNT_AT_ONCE`: **한 번에 리필되는 토큰 개수**
- `TOKEN_REFILL_DURATION_MINUTES`: **토큰 리필 주기(분 단위)**  

`RateLimitingBucketProvider` 객체의 `generateBucket` 메서드로

각각의 클라이언트에 대해서 **분당 20개의 트래픽 제한이 있도록 설정**할 수 있습니다.  

<br>

### 인터셉터의 동작

다시 돌아와서, 인터셉터 로직을 살펴보겠습니다.  

![인터셉터 흐름](https://github.com/hbkuk/now-back/assets/109803585/b75981f7-258d-4cec-8e21-3cd8571289ba)


- **매 요청마다 클라이언트의 IP 확인** (단. preflight에 대해서는 skip)
- **IP 주소와 매칭되는 모든 버킷을 관리하는 객체를 통해 IP주소와 매칭되는 버킷을 확인**
- **IP 주소와 매칭되는 버킷을 가져온 후 토큰을 소비하고 남은 토큰의 양과 함께 ConsumptionProbe 객체를 반환** 
-  **Rate Limit을 초과한 경우 예외를 던지고, 그렇지 않은 경우 요청을 처리**  

```
// RateLimitingInterceptor.java
/**
 * Rate Limiting을 적용하는 인터셉터
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RateLimitingInterceptor implements HandlerInterceptor {

    private final RateLimitBucketMap rateLimitBucketMap;
    private final RateLimitingBucketProvider rateLimitingBucketProvider;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        if (shouldSkipRequest(request.getMethod())) {
            return true;
        }

        String ipAddress = request.getRemoteAddr();
        if (!rateLimitBucketMap.hasBucket(ipAddress)) {
            Bucket newBucket = rateLimitingBucketProvider.generateBucket();
            rateLimitBucketMap.addBucket(ipAddress, newBucket);
        }

        Bucket bucket = rateLimitBucketMap.getBucket(ipAddress);
        ConsumptionProbe probe = Objects.requireNonNull(bucket).tryConsumeAndReturnRemaining(1);

        if (probe.isConsumed()) {
            return true;
        }
        throw new TooManyRequestsException(probe.getNanosToWaitForRefill());
    }

    /**
     * Skip 가능하다면 true 반환, 그렇지 않다면 false 반환(GET 및 OPTIONS 요청인 경우 true)
     *
     * @param httpMethod HTTP 요청 메서드
     * @return Skip 가능하다면 true 반환, 그렇지 않다면 false 반환(GET 및 OPTIONS 요청인 경우 true)
     */
    private boolean shouldSkipRequest(String httpMethod) {
        return isOptionMethod(httpMethod);
    }

    /**
     * HTTP 요청 메서드가 OPTIONS인지 확인
     *
     * @param httpMethod 확인할 HTTP 요청 메서드
     * @return HTTP 요청 메서드가 OPTIONS인 경우 true, 그렇지 않은 경우 false
     */
    private boolean isOptionMethod(String httpMethod) {
        return HttpMethod.valueOf(httpMethod) == HttpMethod.OPTIONS;
    }
}

```

<br>  

자 이제, 위에서 설명한 **`RateLimitingInterceptor`의 동작**과 **Token Refill 시간 이후에 요청이 정상적으로 동작하는지 검증하는 mockMvc기반 테스트 코드**를 살펴보고 마무리 하겠습니다.  

<br>

### Rate Limiting Interceptor에 대한 테스트 코드  

![Rate Limit 테스트 코드 1](https://github.com/hbkuk/now-back/assets/109803585/227bfea7-da63-441f-be58-475a8f5122a6)  

for 루프를 통해 **지정된 엔드포인트 경로로 GET 요청을 생성하고 수행**하는데요.  

**상수 MAX_BANDWIDTH 만큼은 정상적으로 상태 코드 200을 반환**하지만, **이후 요청**에 있어서는 **상태 코드 429를 반환하는 것을 확인**할 수 있습니다.  

<br>


![Rate Limit 테스트 코드 2](https://github.com/hbkuk/now-back/assets/109803585/8993c70f-5529-439f-83ab-3d99597df26b)

해당 테스트 메서드 또한, for 루프를 사용하여 **지정된 엔드포인트 경로로 GET 요청을 생성하고 수행**합니다.  

초기에는 **상수 MAX_BANDWIDTH 횟수만큼의 요청을 보내면 정상적으로 상태 코드 200을 반환**하지만, 이후의 요청에서는 **Rate Limit이 초과되어 상태 코드 429(Too Many Requests)를 반환함을 확인**합니다.

또한, **리필이 된 후에는 동일한 엔드포인트 경로로 GET 요청을 다시 생성하고 수행**하며, 이때는 정상적으로 **상태 코드 200을 반환**합니다.  


#### 테스트 성공

![테스트 성공](https://github.com/hbkuk/now-front/assets/109803585/49e1994e-c242-49e8-b255-dd9e51835bd3)

## 마무리

현재 프로젝트에서 Rate Limit를 적용하게 된 이유와 적용한 내용을 간략하게나마 설명드렸습니다.  

부족하거나, 개선할 부분은 앞으로 프로젝트를 진행하면서 차근차근 진행하고자 합니다.  

긴 글 읽어주셔서 감사합니다.

</div>