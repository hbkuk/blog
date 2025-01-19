<div class=markdown-body>

# 동기(Synchronous)/비동기(Asynchronous) & 블로킹(Blocking)/논블로킹(Non-Blocking)

우선 간단하게 요약해보겠습니다.

동기/비동기를 구분하는 기준으로 **작업의 수행 순서**이고,  
블로킹/논블로킹을 구분하는 기준 **작업의 차단 여부**입니다.

조금 더 풀어서 설명해보자면 아래와 같이 설명할 수 있겠네요.

- **동기** : 일을 하나씩 시키겠다.
- **비동기** : 일을 동시에 여러개 시키겠다.


- **블로킹**: 일을 하나만 시키고, 기다리겠다.
- **논블로킹**: 일을 하나 시키고, 기다리지 않겠다.

내용을 봐도 전혀 와닿지 않을 수 있는데요.  
해당 포스팅을 다 읽고나면 어떤 의미인지 이해할 수 있지 않을까요?  

---

### 동기/비동기란?

**동기(Synchronous)**
- 약어: `Sync`
- 특징: 작업을 순차적으로 실행
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

    - 정리
        - `Task A`가  완료된 후 `Task B`를 실행
            - `Main Thread` 는 하나씩 일을 시키고 있음.

**비동기(Asynchronous)**
- 약어: `Async`
- 특징: 작업을 동시에 여러개 실행
- 예시 코드:

    ```java
    public class AsynchronousExample {
        public static void main(String[] args) {
            TaskA taskA = new TaskA();
            TaskB taskB = new TaskB();
    
            Thread threadA = new Thread(taskA);
            Thread threadB = new Thread(taskB);
    
            threadA.start(); // Task A 실행 시작
            threadB.start(); // Task A 실행 시킨 후 곧바로 실행
        }
    }
    ```

    - 정리
        - `Main Thread` 가 `Task A`와 `Task B` 를 동시에 실행
            - `Main Thread` 는 동시에 일을 시키고 있음.

---

### 블로킹/논블로킹이란?

**블로킹(Blocking)**
- 뜻: 작업이 완료될 때까지 대기하는 방식
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

    - 정리
        - `Main Thread`가 `Task A` 와 `Task B`의 작업 완료를 대기하고 있음
            - `Main Thread` 는 하나의 일을 시키고 대기하고 있음

**논블로킹(Non-Blocking)**
- 뜻: 작업이 완료되지 않아도 대기하지 않음
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

    - 정리
        - `Main Thread` 는 `Task A`와 `Task B`의 작업 결과를 기다리지 않고 종료
            - `Main Thread` 는 일을 시키고 대기하지 않음

결국엔 비슷한 말을 하고 있는 것 같지만, 다시 정리해보겠습니다.

동기/비동기를 구분하는 기준으로 **작업의 수행 순서**입니다.

- 동기 : 일을 하나씩 시키겠다.
- 비동기 : 일을 한번에 여러개 시키겠다.

블로킹/논블로킹을 구분하는 기준 **작업의 차단 여부**입니다.

- 블로킹 : 일을 하나만 시키고, 기다리겠다.
- 논블로킹: 일을 하나 시키고, 기다리지 않겠다.

### 참고
- https://evan-moon.github.io/2019/09/19/sync-async-blocking-non-blocking/

</div>