<div class=markdown-body>

## [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.

<br>

### Cache를 적용하게 된 이유

Cache를 적용하기 전, **수백 명이 동시에 메인 페이지로 접속할 경우에 대해서 생각**해보았습니다.

![메인페이지](https://github.com/hbkuk/blog/assets/109803585/93333a7d-ece0-4a79-b8b7-e6d8df31b9e0)

<br>  

**수백 명의 사용자는 게시물 목록을 가져오는 요청**을 보낼 것이고, 아래 핸들러 메서드가 **수백 개의 쓰레드(Thread)에 의해 실행**될 것입니다.

![모든 게시물 반환 핸들러 메서드](https://github.com/hbkuk/blog/assets/109803585/ac475e51-9fda-446f-b646-8bdd5e57af03)

<br>

이로 인해 **트래픽이 급격하게 증가**하게 되며, 이는 **주로 WAS(Web Application Server)와 데이터베이스(DB) 간의 통신량이 급증하는 것을 의미**합니다.

(아래는 모든 게시물 목록을 가져올때 실행되는 쿼리입니다.)

![모든 게시물을 가져오는 쿼리](https://github.com/hbkuk/blog/assets/109803585/eb8d383f-d5a6-4896-96b3-d14e086d2231)

<br>

이에 따라, 우선적으로 현재 상황에서 부하를 최소화 하기 위한 방법으로 쿼리 최적화보다는 **자주 요청되는 쿼리 결과를 Cahce하여 서버 응답 성능을 향상**시키고자 했습니다.  

<br>

### Spring Cache 종류 

**Spring Cache는 Application Level에서 쉽게 캐시를 구현하고 관리할 수 있도록 다양한 캐시 매니저(캐시 구현체)를 지원**하고 있는데요.  

- **`SimpleCacheManager`**: **메모리 내에서 간단한 캐시를 관리하며 스프링 캐시 추상화를 제공**합니다. 주로 간단한 애플리케이션 또는 개발 및 테스트 목적으로 사용됩니다. 설정이 간단하며 별도의 캐시 저장소나 설정을 필요로하지 않습니다.

- **`ConcurrentMapCacheManager`**: 기본적으로 **ConcurrentHashMap을 사용하여 메모리 내 캐시를 관리**합니다. 주로 간단한 애플리케이션에서 사용될 수 있습니다.

- **`EhCacheCacheManager`**: Ehcache를 기반으로 하는 캐시 매니저로, **메모리 외부에 캐시를 저장**할 수 있도록 해줍니다. 복잡한 캐싱 시나리오에서 사용될 수 있습니다.

- **`CaffeineCacheManager`**: Caffeine을 사용하여 캐시를 관리하는 매니저로, **메모리 내 캐시를 효율적으로 관리하며 최신 기술을 활용**할 수 있습니다.

- **`RedisCacheManager`**: **Redis 데이터베이스를 이용하여 캐싱하는 매니저**로, **분산 환경에서 데이터를 저장하고 관리하는 데 용이**합니다.

- **`GemfireCacheManager`**: Pivotal GemFire를 기반으로 하는 캐시 매니저로, **대규모 분산 캐싱 시나리오에 사용**될 수 있습니다.  

<br>

현재 진행 중인 프로젝트는 **초기에 예상 사용량이 적을 것이라고 생각**됩니다.  

따라서, **현재 프로젝트에서 간단하게 테스트 할 목적으로 선택한 캐시 매니저는 `SimpleCacheManager`** 입니다.

**추후 정식으로 서비스를 할때에는 `EhCacheCacheManager`로 변경**,  
**여러 인스턴스가 공유해야 하는 캐시 저장소가 필요한 경우에는 `RedisCacheManager`로 전환하는 것을 고려**하고자 합니다.  

<br>

### Spring Cache를 사용하기 위한 설정  

#### 의존성 

```
dependencies {
    ...
    implementation 'org.springframework.boot:spring-boot-starter-cache'
}
```  

#### Bean 설정  

![ConcurrentMapCache의 공식문서](https://github.com/hbkuk/blog/assets/109803585/8c4dbce8-dcd9-4933-999f-4d3e1b99f6ee)

**`ConcurrentMapCache` 객체를 생성할 때 Cache의 이름을 전달**하면 됩니다.  

이렇게 이름을 전달하면 **해당 Cache가 생성되고 관리**됩니다.  

<br>

![Cache Bean 설정](https://github.com/hbkuk/blog/assets/109803585/82830efb-112d-457f-b926-7a940b6477ba)  

현재 프로젝트에서는, **게시글(Post) 관련 도메인 객체(Notice, Community, Photo, Inquiry)를 중심으로 Cache를 구현**하고자 합니다. 따라서 위와 같이 설정을 했습니다.  

<br>

#### 서비스 레이어에서 Cahce 적용  

![모든 게시물 반환 핸들러 메서드](https://github.com/hbkuk/blog/assets/109803585/ac475e51-9fda-446f-b646-8bdd5e57af03)

다음은 앞에서 언급했던 **모든 게시글을 조회 후 응답하는 핸들러 메서드**입니다.  

**`PostService` 객체의 `getAllPosts` 메서드를 호출할 때, Condition 객체를 전달**하고 있는데요.  

<br>  

![서비스 객체](https://github.com/hbkuk/blog/assets/109803585/11f0c467-3669-46a2-be8b-d38ee4cb60f6)

위 메서드에서 확인해야하는 부분은 **`@Cacheable` 어노테이션**입니다.  

앞서 **`ConcurrentMapCache` 객체를 생성할 때 Cache의 이름을 전달한다고 언급**했습니다.  

**`@Cacheable` 어노테이션의 value 속성 값에 Cache의 이름을 설정**하면 됩니다.  

**key 속성에 경우, Cache할 데이터를 식별할 고유한 key값으로 설정**하면됩니다.  

또한, **key값을 설정할 때는 SpEL(Spring Expression Language) 문법을 사용**해야 합니다.  

(현재, 모든 게시물을 가져올때는 Condition 객체 필드중 하나의 필드(maxNumberOfPosts)만 허용하기 때문에 위와 같이 설정했습니다.)

<br>

#### 기존 Cache를 삭제해야하는 상황  

예를 들어, **모든 게시물 목록을 조회해서 Cache를 했다고 가정**해보겠습니다.  

Cache한 직후, **새로운 게시물이 작성되거나 수정, 삭제가 되었다면 Cache에 저장된 모든 게시물의 목록도 변경**되어야 하는데요.  

이때는 해당 Cache의 key에 대한 value를 삭제하면 됩니다.  

**하지만, 이전에 저장했던 key값을 전달받지 않았으므로, 모든 값을 삭제하는 방식을 사용했습니다.**  

![캐시삭제](https://github.com/hbkuk/blog/assets/109803585/c7524118-550d-403a-904e-24f3aa07a9e3)  

<br>

#### 만약 여러개의 필드를 갖는 객체를 Key 값으로 설정할 경우  

**고유한 키 값으로 생성하기 위해서는 해당 필드들을 묶어서 key 값으로 설정**할 수 있는데요.  
![복합키](https://github.com/hbkuk/blog/assets/109803585/73531c09-9391-4660-9e92-d828f0aea125)  

이렇게 하는 것 보다는 **`Object` 클래스의 `hashCode()` 메서드를 overriding해서 메서드의 반환 값으로 key값을 설정**할 수 있습니다.  

![hashcode키](https://github.com/hbkuk/blog/assets/109803585/86f26ae8-5c61-4a0f-9d3c-12f2fbf816ba)  

<br>

이렇게 하게 되면 **서비스 레이어에서는 동일한 파라미터 요청에 대해 고유한 key값으로 Cache를 설정**할 수 있습니다.  

<br>

#### 주기적으로 모든 Cache 삭제

또한, **`ConcurrentCache` 객체는 만료 시간을 설정하고 해당 시간이 지나면 자동으로 삭제되는 기능은 제공되지 않습니다.** 
따라서, **Spring Scheduling(스케줄링)**을 사용하여 주기적으로 **모든 캐시를 삭제하는 방식으로 동작**하게 설정 했습니다.  

```
// Spring Cache 관련 Bean 설정
@Configuration
@EnableCaching  // Spring 캐싱 기능을 사용하기 위한 어노테이션
@EnableScheduling  // 스케줄링 기능을 사용하기 위한 어노테이션
@Slf4j  // 로깅을 위한 어노테이션
public class CachingConfig {

    ...

    /**
     * 모든 캐시 삭제
     */
    public void evictAllCaches() {
        // 모든 캐시를 순회하며 각 캐시를 비웁니다
        cacheManager().getCacheNames()
                .forEach(cacheName -> Objects.requireNonNull(cacheManager().getCache(cacheName)).clear());
    }

    /**
     * 주기적으로 모든 캐시를 삭제하는 스케줄링
     */
    @Scheduled(fixedRate = 300000)  // 300초마다 실행
    public void evictAllCachesAtIntervals() {
        evictAllCaches();
    }
}
```  

## 마무리

현재 프로젝트에서 Cache를 적용하게 된 이유와 Spring Cache 적용방법을 간략하게나마 설명드렸습니다.  

부족하거나, 개선할 부분은 앞으로 프로젝트를 진행하면서 차근차근 진행하고자 합니다.  

긴 글 읽어주셔서 감사합니다.

</div>