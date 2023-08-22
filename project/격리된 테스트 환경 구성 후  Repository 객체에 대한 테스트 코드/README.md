<div class=markdown-body>

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.  

<br>  

## 격리된(Isolated) Repository 테스트  

**모든 비즈니스 로직(도메인, 서비스 레이어)에 대한 테스트를 위해 Mock 라이브러리(Mockito)를 활용**했었습니다.  

<br>

그러나 이러한 방식만으로는 **실제 애플리케이션을 사용하는 과정에서 나타나는 일부 문제를 잡아내기 어려웠던 상황**이 종종 발생했었습니다.  
또한, **매번 UI에 의존하여 데이터가 올바르게 입력되고 표시되는지를 확인**하는 것도 어려웠습니다.  

<br>

이러한 상황이 발생했던 이유는 **Repository 레이어에 대한 테스트를 스킵**했기 때문인데요.  

이를 해결하고자, **격리된 Repository 테스트 환경을 구성하여 테스트를 진행**하기로 했습니다.  

<br>

추가적으로, 격리된 환경으로 구성해야했던 이유는 각 테스트가 독립적으로 실행되어 **다른 테스트와의 데이터 간섭 없이 정확한 검증**을 하고자 했기 때문입니다.  

*(auto_increment 속성은 @Transcational 어노테이션과 관계없이 롤백 되지 않음)*

<br>

### 테스트 격리 방법  

스프링에서는 테스트를 격리하는 여러 방법을 제공하고 있는데요.  

해당 프로젝트에서는 그 중 **`@Sql` 어노테이션을 활용해서 격리된 테스트 환경을 구성**했습니다.  

*@Sql:  스프링에서 제공하는 어노테이션으로써, 테스트 클래스에 해당 어노테이션을 붙이면 매 테스트 메소드 실행전 지정된 경로의 SQL 스크립트를 실행*  

<br>

### @RepositoryTest 어노테이션 구현  

테스트의 격리를 더욱 편리하게 처리하기 위해 **`@RepositoryTest`라는 어노테이션을 구현**했습니다.  

![어노테이션 구현](https://github.com/hbkuk/blog/assets/109803585/e1e22aec-dd0a-4d1a-a244-00c606d0d9b5)  

- `@Target(ElementType.TYPE)`: 클래스 레벨에서 사용할 수 있도록 지정
- `@Retention(RetentionPolicy.RUNTIME)`: 런타임까지 어노테이션 정보가 유지되도록 설정
- `@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)`: 랜덤한 포트를 사용하는 Spring Boot 테스트 환경 설정
- `@Sql("${test-scripts.sql-path}")`: ${test-scripts.sql-path}로 **지정된 경로의 SQL 스크립트를 실행**
- `@ActiveProfiles("test")`: "test" 프로파일 활성화  

<br>

**`${test-scripts.sql-path}`의 경우, ${} 안에 있는 test-scripts.sql-path는 설정 파일에 정의된 test-scripts 섹션의 sql-path 프로퍼티 값을 의미**합니다.  
따라서, 실행할 스크립트를 application.yml에 아래와 같이 설정했습니다.

```

...
test-scripts:
  sql-path: "classpath:testdb.sql"
```  

<br>

해당 스크립트는 resources 폴더에 위치시켰습니다.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/b57ac7cf-5595-447f-8268-2478bc22486f" alt="text" width="number" />
</p>

<br>

### 격리된 테스트 환경 구성 후 테스트  


![테스트 코드 정의](https://github.com/hbkuk/blog/assets/109803585/b88f70ed-9972-47c9-971e-5da1b8145759)  

앞서 언급한 `@RepositoryTest` 어노테이션을 사용했습니다.  

<br>

![테스트 코드](https://github.com/hbkuk/blog/assets/109803585/ae52ef9f-7449-4694-af1e-75c2d99b1924)  

따라서, 메서드 실행 전 데이터베이스를 초기화하는 작업을 수행함으로써 각 테스트를 격리시켰습니다.  

<br>  

### 마무리  

@RepositoryTest 어노테이션을 테스트 클래스에 적용함으로써, 테스트 환경을 간편하게 구성할 수 있었습니다. 앞으로 이 어노테이션으로 격리된 테스트 환경을 구성하고 초기 데이터를 로드하는 등의 작업을 더욱 간편하게 처리할 수 있을 것입니다.

부족하거나, 개선할 부분은 앞으로 프로젝트를 진행하면서 차근차근 진행하고자 합니다.  

긴 글 읽어주셔서 감사합니다.


</div>