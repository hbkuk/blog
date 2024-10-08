<div class="markdown-body">

# 순차 처리로 인한 네트워크 트래픽 문제, Queue 기반 스케줄링으로 70% 감소

기술 블로그의 게시글을 한번에 볼 수 있는 [서비스](https://www.techposts.co.kr/)를 운영하고 있습니다.

서비스 이용자분들에게 최신의 게시글을 보여드리기 위해서, 하루 간격으로 RSS를 제공하는 블로그의 게시글을 수집하고 있습니다.

수집하는 작업은 아래와 같이 `Spring Scheduler`를 통해서 구현했는데요.(궁금하신 분들은 아래 코드를 참고해주세요.)

![image](https://github.com/user-attachments/assets/545eb449-45ea-4b9d-ae0b-4d8c4583c0d9)  

매일 동시간대에 19개의 블로그를 순차적으로 수집하다보니, 트래픽이 급격하게 증가하는 현상이 지속적으로 발생했습니다.

- Network In
![image](https://github.com/user-attachments/assets/ff476c98-375b-4327-9678-fb13a2ac68ed)

- Network Out
![image](https://github.com/user-attachments/assets/53f3e378-97fe-4c06-9ea2-c1b8d5760b72)

피크 트래픽이라고 하기엔 다소 낮은 수치일 수도 있습니다. (수치를 직접 확인해보고 싶으신 분들은 아래 내용을 참고해 주세요.)
```
600 Kbps = 600,000 bits per second ÷ 8 = 75 KBps (킬로바이트 퍼 세컨드)
예시 1) 텍스트 파일: 75KB는 약 30~40 페이지의 일반적인 텍스트 문서 크기 정도
예시 2) 이미지 파일: 저화질의 작은 이미지 한 개 정도 
```

정말 작은 트래픽이지만, 제가 이 상황을 '네트워크 트래픽 문제' 라고 정의한 이유는 아래와 같습니다.

1. 현재보다 더 많은 블로그의 게시글을 수집할 예정입니다.
2. 외부 API 연동을 통한 기능이 추가될 예정입니다.
3. 사용자 증가로 인한 트래픽 증가가 예상됩니다.
 
따라서, 해당 문제를 해결할 수 있는 방법을 도출해보고 적절한 방법을 적용해보는 것이 중요하다고 생각했습니다.  

해당 포스팅에서는 급격히 증가하는 트래픽 현상의 원인 분석 후, 이를 해결하기 위해 시도했던 방법에 대해서 상세히 다룰 예정입니다.

## 트래픽 증가 원인 분석

위에서 언급했던, "트래픽이 증가했다" 라는 말은 무엇을 의미하고, 왜 증가했던 것일까요 ?

이 내용을 설명드리기 위해서는, 현재 서비스에서 블로그의 게시글을 수집하는 과정에 대한 설명이 필요합니다.  
아래 간단하게 표현해보았습니다.  

![image](https://github.com/user-attachments/assets/ffcc969a-274c-475e-8e34-3391068c8fa2)
1. 서버(My Server)가 특정 기술 블로그의 RSS Feed에 대해 `HTTP GET` 요청을 전송합니다.  
2. 특정 기술 블로그가 응답한 RSS 데이터를 `Stream` 형태로 수신합니다.
3. 데이터베이스에 저장된 게시글과 중복 저장되지 않도록, 마지막 발행일자를 조회하기 위한 데이터베이스 쿼리를 실행합니다.
4. 데이터베이스에서 조회된 결과를 수신합니다.
5. 새로운 게시글을 데이터베이스에 저장하는 쿼리를 실행합니다.

위 내용을 네트워크 트래픽 관점으로 분류해보면 아래와 같습니다.  

**Network In(인바운드 트래픽)**    
② 특정 기술 블로그로부터 RSS Feed 데이터를 `Stream` 형태로 수신할 때 발생  
④ 데이터베이스에서 조회된 마지막 발행일자를 수신할 때 발생

**Network Out(아웃바운드 트래픽)**  
① 서버(My Server)에서 특정 기술 블로그에 `HTTP GET` 요청을 보낼 때 발생  
③ 데이터베이스에 마지막 발행일자를 조회하는 쿼리를 보낼 때 발생  
⑤ 새로운 게시글을 데이터베이스에 저장하는 쿼리를 보낼 때 발생

위와 같은 과정이 매일 동시간대에 19번 반복됨에 있어서, 네트워크 리소스 사용량이 급격히 증가함에 따라 트래픽이 급격하게 증가하는 현상이 발생했었습니다.  

원인 분석은 이정도로 마무리하면 될 것 같은데요. 그렇다면 이 문제를 어떻게 해결할 수 있을까요?

## 문제 해결을 위한 방법 도출

저는 아래와 같이 3가지 접근 방법을 고민해보았는데요.

1. `Queue` 기반 스케줄링 적용: 동시다발적이 아닌, 분산적으로 처리하여 피크 트래픽 감소 
2. `Worker` 인스턴스 분리: Worker 인스턴스(AWS 예약/스팟 인스턴스 등)를 추가해서 별도 처리
3. `Queue` 시스템(RabbitMQ, kafka, SQS) 적용: 작업을 외부로 분리하여 서버 부하 분산 및 확장성 향상


2번과 3번의 경우 트래픽이 폭발적으로 증가하지 않은 상태라서 굳이 추가적인 서버 관리 비용이나 복잡한 시스템을 도입할 필요는 없을 것 같은데요.    
따라서, 1번 방법이 가장 실용적인 방법이라고 판단했습니다.


## `Queue` 기반 스케줄링 적용하기

제가 생각한 `Queue`를 활용한 스케줄링 방식은 무엇일까요?  
해당 방식을 그림으로 표현하면 아래와 같습니다.  

![image](https://github.com/user-attachments/assets/a194973c-c242-4214-8ba5-fc5d0032d702)
1. 매일 새벽 3시에 `Queue`를 초기화하는 스케줄러가 실행되며, 수집할 블로그 19개가 `Queue`에 추가됩니다.
2. 매일 새벽 3시부터 5시까지 5분 간격으로 `Queue`에서 꺼내서 RSS Feed를 읽는 스케줄러가 실행됩니다.

![image](https://github.com/user-attachments/assets/5f04e146-c4b4-47cb-abbf-04684eac1615)

아래 코드를 배포 후 2일 정도 시간을 두고 모니터링해보았는데요.  
확인해보니 피크 트래픽이 `600Kbps`에서 `200Kbps`로 `66.67%(약 70%)` 감소했습니다.

### Network In

- **분산 처리 전**
![image](https://github.com/user-attachments/assets/7288834f-baa6-42f0-8911-be7ee0f621bb)
  - 피크 트래픽: 약 `600Kbps`

- **분산 처리 후**
![image](https://github.com/user-attachments/assets/2834952f-da68-443a-bcb7-f2c12c60609a)
  - 피크 트래픽: 약 `200Kbps`

### Network Out
- **분산 처리 전**
  ![image](https://github.com/user-attachments/assets/bf855c1a-5ad1-4bf5-ac91-2736642227c6)
  - 피크 트래픽: 약 `600Kbps`

- **분산 처리 후**
![image](https://github.com/user-attachments/assets/4b8a2a10-3546-4bae-90dc-cc723d46e680)
- 피크 트래픽: 약 `200Kbps`

트래픽이 약 70% 감소한 정확한 이유를 설명하기 위해서는 더 자세한 데이터 분석이 필요하지만, 저는 네트워크 리소스가 획복될 시간이 생겨서 트래픽이 감소했을 것이라고 추측하고 있습니다.      
향후 더 정확한 분석을 위해서 추가적인 모니터링해보려고 합니다.  

### 정리

지금까지 `스케줄러 기반 순차 처리 시 발생하는 네트워크 트래픽 문제 해결` 경험에 대해서 공유해드렸습니다.  
다소 낮은 트래픽에서 개선한 경험이지만, 처음으로 서비스를 배포 후 모니터링을 통해서 성능을 개선했다는 점에서 충분히 만족합니다.

앞으로 서비스가 더 확장됨에 따라, 저 또한 기술적인 문제를 천천히 해결해 나아가보려고 합니다.

긴 글 읽어주셔서 감사드립니다 :)


</div>