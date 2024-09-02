<div class="markdown-body">

# Offset Based Pagination 성능 이슈 해결하기

기술 블로그의 게시글을 한번에 볼 수 있는 [서비스](https://www.techposts.co.kr/)를 운영하고 있습니다.  

현재 많은 사용자가 이용하고 있는 건 아니지만, 앞으로 서비스를 지속적으로 유지하기 위해서는 지출되는 비용을 최대한 절감하는 것이 중요하다고 생각했어요.  
그 중에서도 데이터베이스 성능 이슈를 발견했었고, 이를 해결하고자 합니다.

성능 이슈가 발생했던 시점에는, 아래와 같이 페이지 번호를 보여주고 있습니다.
![image](https://github.com/user-attachments/assets/316cb80a-b9b7-43fe-bdc3-dcb972a0a0f7)

클라이언트가 페이지 번호를 클릭할 때마다, 데이터베이스 쿼리가 실행되는 속도를 확인해봤어요.
![image](https://github.com/user-attachments/assets/c5b58930-57a9-490c-bd94-c220932ec4f2)

사용자 경험 혹은 리소스 사용 측면에서 봤을 때, 원인을 찾아서 해결해야 하는 것이 중요하다고 생각했습니다.  
해당 포스팅에서는 데이터베이스 성능 이슈를 발견하고, 이를 개선하기 위해 시도했던 방법에 대해서 상세히 다룰 예정입니다.

## 프로젝트 배경

우선, 성능 이슈가 발생했던 테이블 구조와 쿼리를 확인해보겠습니다.

#### 테이블 구조
```
create table post
(
    id          bigint      not null auto_increment,
    blog        varchar(10),
    link        varchar(255),
    publish_at  datetime(6),
    title       varchar(100),
    primary key (id)
) engine = InnoDB;
```

#### 쿼리

```
SELECT p1_0.id,
       p1_0.blog,
       p1_0.link,
       p1_0.publish_at,
       p1_0.title
FROM post p1_0
ORDER BY p1_0.publish_at DESC
LIMIT 100, 5;
```
이미 많은 분들이 알고 계실 것으로 예상되는데요. 위 쿼리는 오프셋 기반 페이지네이션(`Offset Based Pagination`)을 구현할 때 흔히 사용되는 쿼리 형식입니다.    
흔히 사용되는 쿼리 형식인데, 어떤 이유로 성능 이슈가 발생하는 것일까요?

## 원인 찾기 - 실행 계획 분석

MySQL 기준, `EXPLAIN` 명령어를 통해서 쿼리 실행 계획을 살펴보았습니다.   
(`EXPLAIN` 명령어에 대해서 더 자세한 내용이 궁금하신 분은 [링크](https://0soo.tistory.com/235)를 참고해주세요.)

![image](https://github.com/user-attachments/assets/092b7813-67b8-4a6e-bd62-2fbd0ab1451e)

위 실행 계획을 정리해보겠습니다. 

- 풀 테이블 스캔 (`type: ALL`) 
  - 테이블 전체를 스캔하고 있으며, 인덱스가 전혀 사용되지 않고 있음.
- 인덱스 부재 (`possible_keys: null`)
  - 적절한 인덱스가 없기 때문에, 쿼리가 인덱스를 사용하지 못하고 있음.
- 파일 정렬 (`Extra: Using filesort`)
  - 메모리 내에서 정렬이 이루어지지 않고 디스크에 임시 파일을 생성해 정렬이 수행되고 있음.

쿼리에서 인덱스를 사용하도록 한다면, 성능 이슈가 해결되지 않을까요?

## 성능 이슈를 해결하기 위한 방법 도출

### 1. 인덱스 적용

위 실행 계획을 분석한 내용을 살펴보았을 때, 인덱스를 사용하지 못하고 있으므로 `ORDER BY` 절에 사용된 `publish_at` 컬럼에 대해 인덱스를 사용할 수 있게 생성해보겠습니다.

```
CREATE INDEX idx_post_publish_at_desc ON post (publish_at DESC);
```

인덱스를 적용하고 실행 계획을 다시 살펴볼게요.

![image](https://github.com/user-attachments/assets/092b7813-67b8-4a6e-bd62-2fbd0ab1451e)

분명 `ORDER BY` 절에 사용된 `publish_at` 컬럼에 대한 인덱스를 추가해주었는데, 인덱스를 제대로 사용하지 못하고 있습니다.

어떤 이유일까요? 옵티마이저는 왜 이런 결정을 내렸을까요?

---

### 옵티마이저가 인덱스를 사용하지 않은 이유

우선 `ORDER BY` 절에 `publish_at` 컬럼이 아닌, PK(Primary Key)인 `id` 컬럼을 적용해서 실행 계획을 살펴보겠습니다.

```
EXPLAIN SELECT p1_0.id,
       p1_0.blog,
       p1_0.link,
       p1_0.publish_at,
       p1_0.title
FROM post p1_0
ORDER BY p1_0.id DESC
LIMIT 100, 5;
```

![image](https://github.com/user-attachments/assets/13fd5d09-77c9-4fef-8dc3-5acfcc69a43f)

위 실행 계획을 분석해보면, 인덱스를 반대로 스캔하여 데이터를 조회하고 있는 것을 확인할 수 있습니다.  

이해를 돕기위해, 아주 간단하게 그림으로 표현해보았습니다.   
(클러스터드 인덱스(Clustered Index), 비클러스터드 인덱스(Non-Clustered Index) 개념에 대해서 생소하신 분들은 [링크](https://hudi.blog/db-clustered-and-non-clustered-index) 참고해주세요.)

![image](https://github.com/user-attachments/assets/7627a204-267d-4c4e-9fb0-39560dcc5cf1)

옵티마이저는 클러스터드 인덱스에서 물리적인 데이터 페이지(리프 페이지)가 잘 정렬되어 있으니, 이를 활용해서 조회하고 있는 것으로 확인할 수 있습니다.

반면 위에서 언급되었던 `ORDER BY` 절에 사용된 `publish_at` 컬럼에 대한 인덱스를 추가해주었는데, 왜 인덱스를 사용하지 못했던 것일까요?  
그림으로 살펴볼게요.

![image](https://github.com/user-attachments/assets/bfd80e14-1da0-4228-95a6-cfd60f76c44c)

`publish_at` 컬럼은 잘 정렬되어 있으나, `SELECT` 절에 포함된 다른 컬럼도 추가적으로 조회해야 합니다.

그렇다면 어떻게 조회할 수 있을까요?  

![image](https://github.com/user-attachments/assets/88e14748-3197-4c19-8a2d-90d0d69609c7)

위처럼 비클러스터드 인덱스에서는 클러스터드 인덱스 값을 가지고 있으므로, 이를 통해 다른 컬럼들을 탐색을 하게 됩니다.  

결국에는 비클러스터드 인덱스를 통해서 `publish_at` 컬럼을 조회하고, 클러스터드 인덱스 값을 통해서 클러스터드 인덱스를 조회해야한다는 것인데요.     
옵티마이저 입장에서는 비클러스터드 인덱스를 사용하는 것이 효율적이지 않다고 판단했을 것입니다.  

차라리, 모든 테이블을 스캔 후 `publish_at` 컬럼 기준으로 정렬한 후 데이터를 조회하는 방법이 좋지 않을까요?
(MySQL에서는 이를 `File Sort` 라고 정의하고 있습니다.) 

위 내용들을 정리해볼게요.
1. 클러스터드 인덱스로 쿼리가 실행될 경우 데이터가 물리적으로 정렬되어 있는 인덱스를 사용한다.
2. 비클러스터드 인덱스로 쿼리가 실행될 경우, 다른 컬럼들을 조회하기 위해서는 각 행마다 클러스터드 인덱스를 다시 찾아가야 한다.

옵티마이저는 비클러스터드 인덱스를 사용하는 것보단, 전체 테이블을 스캔 후 `File Sort`를 수행하는 것이 더 효율적이라고 판단했을 것이라고 생각됩니다.  
그렇다면, `SELECT` 절에 있는 모든 컬럼이 비클러스터드 인덱스에 포함되어 있게 인덱스를 생성하면 어떨까요? 

## 2. 커버링 인덱스 적용

잠깐, 실행되는 쿼리를 다시 한번 살펴볼게요.

```
SELECT p1_0.id,
       p1_0.blog,
       p1_0.link,
       p1_0.publish_at,
       p1_0.title
FROM post p1_0
ORDER BY p1_0.publish_at DESC
LIMIT 100, 5;
```

커버링 인덱스를 적용하기 위해서는 아래와 같이 인덱스를 생성해주면 되는데요.  

```
CREATE INDEX idx_post_covering ON post (publish_at, id, blog, link, title);
```

생성 후 바로 실행 계획을 살펴보겠습니다.

![image](https://github.com/user-attachments/assets/7f35196a-b77b-4e50-8ffe-35a644518772)

위에서 생성해주었던 커버링 인덱스를 사용해서 데이터를 조회하고 있는 것을 확인할 수 있습니다.  

이대로 성능 이슈를 해결했다고 정리할 수 있는데요.    
다음 쿼리와 실행 계획을 살펴볼게요.

```
EXPLAIN SELECT p1_0.id,
       p1_0.blog,
       p1_0.link,
       p1_0.publish_at,
       p1_0.title
        FROM
            post p1_0
ORDER BY p1_0.publish_at DESC
LIMIT 4890, 5;
```

![image](https://github.com/user-attachments/assets/43e26c81-21a4-4793-b896-5b5750973c50)

위 실행 계획에서, 접근한 데이터의 행 수를 확인해볼까요?    


도대체 왜 옵티마이저는 모든 행을 다 읽고, 데이터를 반환하는 것일까요?

옵티마이저가 전체 결과셋을 정렬한 후, 필요한 부분만 잘라내는 방식을 선택하기 때문인데요.  
아래 그림으로 살펴볼게요.
![image](https://github.com/user-attachments/assets/06b22fb5-c198-4512-8e29-c1545a10b1d8)

왜 특정 행까지 읽어야 할까요?
- 옵티마이저는 어떤 행이 4891번째부터 4895번째인지 미리 알 수 있는 방법이 없습니다.
- 처음부터 차례대로 읽으면서 카운트해야 합니다.

그렇다면, 데이터 양이 많아지고 `LIMIT`의 오프셋이 커질 경우 성능 이슈가 발생하지 않을까요?

## 3. 커서 기반 페이지네이션(Cursor based Pagination) 적용

옵티마이저가 모든 행을 읽지 않도록 하기 위해서는 "특정 값 이후의 N개를 읽어와"라고 지시를 해야합니다.
이를 위해 커서(Cursor)라는 개념을 사용합니다.

### Cursor(커서)의 개념

커서란 사용자에게 응답해준 데이터 중 가장 마지막 데이터를 식별할 수 있는 `Key`입니다.  
옵티마이저는 `Key`를 기준으로 그 다음 데이터부터 조회를 시작합니다.  
이 방식을 사용하면 오프셋 기반 페이지네이션과는 달리 모든 이전 데이터를 읽을 필요가 없어집니다.

### 커서 설계
커서 설계시 주의해야할 점은 "커서는 유니크해야 한다."라는 것 입니다.

그렇다면, 아래와 같이 `publish_at` 컬럼과 `id` 컬럼을 조합하여 커서를 생성할 수 있는데요.
```
CONCAT(
    LPAD(DATE_FORMAT(p1_0.publish_at, '%Y%m%d%H%i%s'), 20, '0'),
    LPAD(p1_0.id, 10, '0')
) as cursor
```

이 방식은 `publish_at`을 기본 정렬 기준으로 사용하고,  
동일한 `publish_at` 값이 있을 경우 `id`로 추가 정렬하여 유니크성을 보장하고 있습니다.

그렇다면, 커서 기반 페이지네이션을 적용한 쿼리를 확인해볼까요?

```
EXPLAIN SELECT p1_0.id,
               p1_0.blog,
               p1_0.link,
               p1_0.publish_at,
               p1_0.title,
               CONCAT(
                       LPAD(DATE_FORMAT(p1_0.publish_at, '%Y%m%d%H%i%s'), 20, '0'),
                       LPAD(p1_0.id, 10, '0')
               ) as curosr
        FROM
            post p1_0
        WHERE
            CONCAT(
                    LPAD(DATE_FORMAT(p1_0.publish_at, '%Y%m%d%H%i%s'), 20, '0'),
                    LPAD(p1_0.id, 10, '0')
            ) > '000000202309111459500000002182'
        ORDER BY p1_0.publish_at DESC
        limit 5;
```

위 쿼리에 대한 실행 계획을 살펴볼게요.

![image](https://github.com/user-attachments/assets/820996a5-dc3f-4a55-a692-ee94538ba917)

인덱스를 효율적으로 사용하고 있음을 확인할 수 있습니다.  
이 방식을 통해 옵티마이저는 전체 데이터셋을 스캔하지 않고도 다음 페이지의 데이터를 가져올 수 있습니다.

### 마무리

지금까지 데이터베이스 성능 이슈를 발견하고, 이를 개선하기 위해 시도했던 방법에 대해서 이야기 해드렸는데요.  
커서 기반 페이지네이션의 구체적인 구현 방법과 Querydsl을 이용한 무한 스크롤 구현에 대해서는 다음 포스팅에서 더 자세히 다루도록 하겠습니다.

긴 글 읽어주셔서 감사드립니다.   
많은 분들에게 제 경험이 도움이 되었기를 바랍니다. :)

### 참고
- [오프셋 페이징이 느린 진짜 이유](https://wonit.tistory.com/664)
- [MySQL의 Using temporary, Using filesort (+ 정렬 방식) 정리!](https://seongonion.tistory.com/158)
- [데이터베이스 인덱스 (2) - 클러스터형 인덱스와 비클러스터형 인덱스](https://hudi.blog/db-clustered-and-non-clustered-index/)

</div>