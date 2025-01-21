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

### 마무리

혹시 충분한 이해가 되셨을까요?  
많이 부족한 글이지만 도움이 되셨길 바랍니다. :)

### 참고
- https://evan-moon.github.io/2019/09/19/sync-async-blocking-non-blocking/

</div>