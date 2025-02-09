<div class=markdown-body>

# 동기(Synchronous)/비동기(Asynchronous) & 블로킹(Blocking)/논블로킹(Non-Blocking)

최근 팀원분의 기술리뷰에서 해당 단어들이 언급되었고, 듣는 순간 머릿속에서 정리가 안되었는데요.  
따라서, 확실하게 정리하고자 해당 포스팅을 작성했습니다.

---

도입부에서 간단하게 요약해보자면 ...

동기/비동기를 구분하는 기준은 **작업의 수행 순서**,  
블로킹/논블로킹을 구분하는 기준은 **작업의 차단 여부** 이라고 말할 수 있습니다.

이를 조금 더 풀어서 설명해보자면 아래와 같이 설명할 수 있겠네요.

- **동기** : 작업이 하나씩 실행
- **비동기** : 작업이 여러개 실행


- **블로킹**: 작업을 시키고, 기다림
- **논블로킹**: 작업을 시키고, 기다리지 않음

그럼 하나씩 살펴보겠습니다.  

---

### 동기/비동기란?

**동기(Synchronous)**
- 약어: `Sync`
- 특징: 작업이 하나씩 실행
- 예시 코드:

    ```java
    public class SynchronousExample {
        public static void main(String[] args) {
            TaskA taskA = new TaskA();
            TaskB taskB = new TaskB();
    
            Thread threadA = new Thread(taskA);
            Thread threadB = new Thread(taskB);
    
            threadA.start(); // Task A 실행
            threadA.join();
            
            threadB.start(); // Task A 종료 후 Task B 실행
            threadB.join();
        }
    }
    ```
    - `Task A`가  완료된 후 `Task B`가 실행

**비동기(Asynchronous)**
- 약어: `Async`
- 특징: 작업이 여러개 실행
- 예시 코드:

    ```java
    public class AsynchronousExample {
        public static void main(String[] args) {
            TaskA taskA = new TaskA();
            TaskB taskB = new TaskB();
    
            Thread threadA = new Thread(taskA);
            Thread threadB = new Thread(taskB);
    
            threadA.start(); // Task A 실행 시작
            threadB.start(); // Task A 실행 후 곧바로 실행
        }
    }
    ```
    - `Task B`가 `Task A` 실행 결과를 기다리지 않고 실행

---

### 블로킹/논블로킹이란?

**블로킹(Blocking)**
- 뜻: 작업을 시키고, 기다림
- 예시:

    ```java
    public class BlockingExample {
        public static void main(String[] args) {
            TaskA taskA = new TaskA();
            TaskB taskB = new TaskB();
    
            Thread threadA = new Thread(taskA);
            Thread threadB = new Thread(taskB);
    
            threadA.start();
            threadA.join();  // Main Thread는 Task A 완료까지 대기
            
            threadB.start();
            threadB.join();  // Main Thread는 Task B 완료까지 대기
        }
    }
    ```
    - `Main Thread`가 `Task A` 와 `Task B`의 작업 완료를 대기하고 있음
        

**논블로킹(Non-Blocking)**
- 뜻: 작업을 시키고, 기다리지 않음
- 예시:

    ```java
    public class NonBlockingExample {
        public static void main(String[] args) {
            TaskA taskA = new TaskA();
            TaskB taskB = new TaskB();
    
            Thread threadA = new Thread(taskA);
            Thread threadB = new Thread(taskB);
    
            System.out.println("Main Thread 시작");
            
            threadA.start(); // Task A 실행 시작
            threadB.start(); // Task B 실행 시작
    
            System.out.println("Main Thread 종료");
        }
    }
    ```
    - `Main Thread` 는 `Task A`와 `Task B`의 작업 결과를 기다리지 않음

### 정리

결국엔 똑같은 말을 하고 있는 것 같지만, 중요한 내용에 대해서 다시 정리해보겠습니다.

동기/비동기를 구분하는 기준으로 **작업의 수행 순서**입니다.  
즉, 각 작업이 하나씩 순차적으로 실행되는지, 아니면 여러 작업이 병렬로 실행되는지에 따라 구분합니다.

- **동기** : 작업이 하나씩 실행
- **비동기** : 작업이 여러개 실행

블로킹/논블로킹을 구분하는 기준 **작업의 차단 여부**입니다.
각 작업을 요청한 후 기다리는지, 아니면 기다리지 않고 다른 작업을 진행하는지에 따라 구분합니다.

- **블로킹**: 작업을 시키고, 기다림
- **논블로킹**: 작업을 시키고, 기다리지 않음

### 조합

위에서 언급된 **동기/비동기**와 **블로킹/논블로킹**은 각각 독립적인 개념이지만, 일반적으로 조합해서 표현합니다.  
이를 조합해볼까요?

**동기 + 블로킹**
- 순차적으로 작업이 진행되고(동기), `Main Thread`는 각 작업이 완료될 때까지 대기(블로킹)
- 실생활 예시: 식당에서 줄 서서 직접 주문하고 (핸드폰 보지 않으면서 앞만 보고) 기다림
- 코드 예시:
```java
  public class SyncBlockingExample {
      public static void main(String[] args) {
          System.out.println("음식 주문");
          
          String food = cookFood();     // Main Thread 대기
          
          System.out.println("음식 받음: " + food);
      }
      
      public static String cookFood() {
          try {
              Thread.sleep(3000);
          } catch (InterruptedException e) {
              e.printStackTrace();
          }
          
          return "치킨";
      }
  }
  
  // 음식 주문
  // 음식 받음: 치킨
```

**동기 + 논블로킹**
- 순차적으로 작업이 진행되고(동기), `Main Thread`는 다른 작업 진행(논블로킹)
- 실생활 예시: 식당에서 줄 서서 직접 주문하고 (진동벨을 받아서) 다른 일을 하면서 기다림
- 코드 예시:
```
  public class SyncNonBlockingExample {
      public static void main(String[] args) {
          System.out.println("음식 주문");
          
          while(!isFoodReady()) { // 음식이 준비될 때까지 계속 확인(Polling)
              System.out.println("음식이 아직 안 나왔네. 1초 후 다시 확인");
              try {
                  System.out.println("핸드폰 보는 중");
                  Thread.sleep(1000);             // 1초 후 다시 확인
              } catch (InterruptedException e) {
                  e.printStackTrace();
              }
          }
          
          System.out.println("음식 받음!");
      }
      
      public static boolean isFoodReady() {
          return Math.random() > 0.8;
      }
  }
  
  // 음식 주문
  // 음식이 아직 안 나왔네. 1초 후 다시 확인
  // 핸드폰 보는 중
  // 음식이 아직 안 나왔네. 1초 후 다시 확인
  // 핸드폰 보는 중
  // 음식 받음!
```

**비동기 + 블로킹**
- 병렬적으로 작업이 진행되고(비동기), `Main Thread`는 완료될 때까지 대기(블로킹)
- 실생활 예시: 여러 개의 요리를 동시에 주문하고, 마지막 요리가 나올 때까지 기다림
- 코드 예시:
```java
  public class AsyncBlockingExample {
      public static void main(String[] args) {
          System.out.println("음식 주문 (치킨, 피자, 파스타)");
          
          // 비동기적으로 여러 개의 요리 주문
          CompletableFuture<String> chicken = CompletableFuture.supplyAsync(() -> cookFood("치킨", 3000));
          CompletableFuture<String> pizza = CompletableFuture.supplyAsync(() -> cookFood("피자", 5000));
          CompletableFuture<String> pasta = CompletableFuture.supplyAsync(() -> cookFood("파스타", 4000));
          
          // 모든 요리가 완료될 때까지 대기 (블로킹 발생)
          CompletableFuture<Void> allOrders = CompletableFuture.allOf(chicken, pizza, pasta);
          try {
              allOrders.get();  // 모든 요리가 완성될 때까지 블로킹
              System.out.println("모든 음식이 준비되었습니다!");
              System.out.println("주문 완료: " + chicken.get() + ", " + pizza.get() + ", " + pasta.get());
          } catch (InterruptedException | ExecutionException e) {
              e.printStackTrace();
          }
      }
      
      // 비동기 요리 함수
      public static String cookFood(String food, int time) {
          try {
              Thread.sleep(time);  // 요리하는 시간 (비동기 실행)
          } catch (InterruptedException e) {
              e.printStackTrace();
          }
          return food;
      }
  }
  
  // 음식 주문 (치킨, 피자, 파스타)
  // 모든 음식이 준비되었습니다!
  // 주문 완료: 치킨, 피자, 파스타
 ```

**비동기 + 논블로킹**
- 병렬적으로 작업이 진행되고(비동기), `Main Thread`는 다른 작업 진행(논블로킹)
- 실생활 예시: 여러 개의 요리를 동시에 주문하고, 요리가 준비되면 종업원이 음식을 가져다줌.
- 코드 예시:
```java
  public class AsyncNonBlockingExample {
      public static void main(String[] args) {
          System.out.println("음식 주문 (치킨, 피자, 파스타)");
          
          // 비동기적으로 여러 개의 요리 주문 후, 콜백을 사용하여 처리
          CompletableFuture.supplyAsync(() -> cookFood("치킨", 3000))
              .thenAccept(food -> System.out.println("음식 받음: " + food));
          
          CompletableFuture.supplyAsync(() -> cookFood("피자", 5000))
              .thenAccept(food -> System.out.println("음식 받음: " + food));
          
          CompletableFuture.supplyAsync(() -> cookFood("파스타", 4000))
              .thenAccept(food -> System.out.println("음식 받음: " + food));
          
          System.out.println("다른 작업 수행 중... (요리가 끝날 때까지 기다리지 않음)");
          
          // 메인 스레드 종료 방지
          try {
              Thread.sleep(6000);
          } catch (InterruptedException e) {
              e.printStackTrace();
          }
      }
      
      public static String cookFood(String food, int time) {
          try {
              Thread.sleep(time);  // 요리하는 시간 (비동기 실행)
          } catch (InterruptedException e) {
              e.printStackTrace();
          }
          return food;
      }
  }
  
  // 음식 주문 (치킨, 피자, 파스타)
  // 다른 작업 수행 중... (요리가 끝날 때까지 기다리지 않음)
  // 음식 받음: 치킨
  // 음식 받음: 파스타
  // 음식 받음: 피자
```

### 정리
1. 동기 + 블로킹: 요청 후 응답을 받을 때까지 기다림
2. 동기 + 논블로킹: 요청 후 주기적으로 상태를 확인
3. 비동기 + 블로킹: 비동기 요청 후 응답을 기다림
4. 비동기 + 논블로킹: 요청 후 응답을 기다리지 않고 콜백 혹은 이벤트로 처리

### 마무리

혹시 충분한 이해가 되셨을까요?  
많이 부족한 글이지만 도움이 되셨길 바랍니다. :)

### 참고
- https://evan-moon.github.io/2019/09/19/sync-async-blocking-non-blocking/

</div>