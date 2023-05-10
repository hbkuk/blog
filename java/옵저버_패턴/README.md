<div class="markdown-body">  

# 옵저버 패턴(Observer Pattern)  

![옵저버 패턴](https://img1.daumcdn.net/thumb/R800x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FSz5Ts%2FbtrFAiT6Nhb%2Fwz09tsSoB6TKmKdV7hgZik%2Fimg.png)  

### 옵저버 패턴이란?  

객체의 상태 변화를 관찰하는 **관찰자들(Observers)의 목록을 객체에 등록**하여 **상태 변화**가 있을 때마다 메서드 등을 통해 객체가 직접 각 **옵저버에게 통지**하도록 하는 디자인 패턴입니다.  

하나의 `Subject`에 여러 `Observer`를 **등록**(register)해 두고, **통지**(notify)를 하게 되면, **루프**(for observer ..)를 순회하면서 각 `Observer`를 **Update**하는 패턴입니다.  

## Observer 인터페이스

`Observer`는 `Subject`에 생긴 변화에 관심을 갖는다.  

```
public interface Observer {
    public void update(Subject theChangedSubject);
}
```  

- `Subject`는 `Observer`들을 알고 있는 객체이다.  
    - 여러 Observer가 Subject에 붙을 수 있다.

## Subject 인터페이스  

```
public interface Subject {
    public void register(Observer o);
    public void unregister(Observer o);
    public void notify();
}
```  
- `register`: Subject에 Observer를 등록한다.
- `unregister`: Subject에 등록한 Observer의 구독을 해지한다.  
- `notify`: Subject에서 모든 Observer에 정보를 전달한다.
   
<br>  

## 옵저버 패턴 사용 예제  

#### 요구사항: 주식 시장에서는 주가 상승과 주가 하락에 변동이 있을 시 구독자들에게 해당 알림을 통지하도록 한다.  

<br>  

`StockMarket Class`:  Observable 클래스를 상속한다.  
- `setChanged()` 메서드를 호출한 다음 `notifyObservers()` 메서드를 호출하여 **옵저버에게 주가 변화를 알린다.**
    - observable 객체가 변경된 것으로 표시하는 데 사용된다.
    - notifyObservers()에 대한 후속 호출이 실제로 옵저버에게 알릴 것임을 의미한다.

```
Public class StockMarket extends Observable {

    public void priceRise() {
        System.out.println("Stock price has risen");
        setChanged();
        notifyObservers("Price has risen");
    }

    public void priceFall() {
        System.out.println("Stock price has gone down");
        setChanged();
        notifyObservers("The price has gone down");
    }
}
```

`Subscriber Class`: update() 메서드 하나만 있는 `Observer` 인터페이스를 구현한다.
-  update() 메서드는 옵저버와 공유할 새로운 정보가 있을 때 Observable 클래스(이 경우 StockMarket의 슈퍼클래스)에 의해 자동으로 호출된다.

```
public class Subscriber implements Observer {
    private String name;

    public Subscriber(String name) {
        this.name = name;
    }

    @Override
    public void update(Observable o, Object arg) {
        String message = (String) arg;
        System.out.println(name + "received. " + message);
    }
}
```  

<br>  


### Observer와 Observable은 Java SE 9 버전부터 Deprecated 되었다.  

이로인해, 자체적으로 **인터페이스 및 클래스를 사용해서 옵저버 패턴을 구현하는 것도 좋은 방법**이다.  

아래 클래스 다이어그램을 보면서 자체적으로 어떻게 구현했는지 보자.  

<br>  

#### 대기 줄 정보를 디스플레이(Observer)가 구독하는 구조로 이루어져 있다.

![클래스 다이어그램](https://github.com/hbkuk/blog/assets/109803585/4e79f3c9-b807-42f7-a506-c2a6caaeea9c)  

<br> 
  
대략적인 **`update()` 호출까지의 흐름**을 그림으로 살펴보자.  

### line의 변경사항이 등록되면, update() 메서드를 호출한다.

![호출 1](https://github.com/hbkuk/blog/assets/109803585/f0b0e2f7-5c72-4f0b-a749-6028a1c3883e)  

<br>  

### 등록된 Observer 목록을 전체 순회하면서 각각의 Observer의 `update()` 메서드를 호출한다.  

![호출 2](https://github.com/hbkuk/blog/assets/109803585/7e8036b5-048a-401f-947c-5f86e35c99d4)  

<br>  

### `update()` 메서드는 `display()` 메서드를 호출하게 되며, 모든 Observer는 수신된 콘텐츠를 출력한다.

![호출 3](https://github.com/hbkuk/blog/assets/109803585/c7b22590-6fa3-4a3d-bf97-f7590d3ad5a7)  

<br>  

### 전체적인 흐름은 이해했으리라 생각된다.  

이제 구현한 코드를 보면서 깊게 이해해보자.  

먼저 Observer와 Subject 인터페이스를 보자.
- `update()` 메소드의 인자로 Subject가 아니라 각 값을 전달한다는 점이 다르다.
- 더욱 느슨한 결합을 선호하며, 전달해야 할 값이 적다면 해당 방법으로 설계해도 괜찮다고 생각한다.  

```
public interface Observer {
    void update( int currentNumber, int totalNumber);
}
```
```
public interface Subject {
    void registerObserver(Observer o);
    void removeObserver(Observer o);
    void notifyObservers();
}
```  

다음은 Subject의 구현체이다.  

변경이 발생할 때, Subject에서 알림을 호출한다.  

```
public class LineData implements Subject {
    private List<Observer> observers;
    private int currentNumber;
    private int totalNumber;

    public LineData() {
        this.observers = new ArrayList<>();
    }

    @Override
    public void registerObserver(Observer o) {
        observers.add(o);
    }

    @Override
    public void removeObserver(Observer o) {
        int i = observers.indexOf(o);
        if (i >= 0) {
            observers.remove(i);
        }
    }

    @Override
    public void notifyObservers() {
        for( Observer observer : observers ) {
            observer.update(currentNumber, totalNumber);
        }
    }

    public void lineChanged() {
        notifyObservers();
    }

    public void setLine(int currentNumber, int totalNumber) {
        this.currentNumber = currentNumber;
        this.totalNumber = totalNumber;
        lineChanged();  // 변경이 발생할 때, 알림을 돌리는 방법 선택
    }
}
```  

Display를 위한 인터페이스이다.  

```
public interface DisplayElement {
    void display();
}
```  

그리고 Observer 구현체.

`update()` 메서드가 호출될 때 마다, `display()` 메서드가 호출되어 화면을 출력하도록 설정되어있다.  

생성자를 통해 파라미터로 받은 Subject에 자기 자신인 `this`을 등록하기 때문에 `main()` 메소드에서 Subject에 옵저버를 일일이 등록하지 않는다.  

```
public class CurrentLineCondition implements DisplayElement, Observer {
    private int myNumber;
    private int currentNumber;
    private int totalNumber;
    private Subject lineData;

    public CurrentLineCondition(int myNumber, Subject turnData) {
        this.myNumber = myNumber;
        this.lineData = turnData;
        turnData.registerObserver(this);
    }

    @Override
    public void update(int waitingNumber, int totalNumber) {
        this.currentNumber = waitingNumber;
        this.totalNumber = totalNumber;
        display();
    }

    @Override
    public void display() {
        System.out.println(
                String.format("나의 순번: %d, 대기 순번: %d번, 총 순번: %d번",
                        myNumber, currentNumber, totalNumber));
    }
}
```  
테스트를 위해 작성한 main 메소드이다.  

```
public class Application {
    public static void main(String[] args) {
        LineData line = new LineData();
        CurrentLineCondition current1 = new CurrentLineCondition(30, line);
        CurrentLineCondition current2 = new CurrentLineCondition(40, line);
        CurrentLineCondition current3 = new CurrentLineCondition(50, line);

        line.setLine(20, 100);
        line.setLine(21, 100);
        line.setLine(22, 100);
    }
}
```  

</div>