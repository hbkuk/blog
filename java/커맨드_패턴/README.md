<div class="markdown-body">  

# 커맨드 패턴(Command Pattern)  

실행될 기능을 **캡슐화**함으로써 주어진 여러 기능을 실행할 수 있는 재사용성이 높은 클래스를 설계하는 패턴이다.  

- 실행할 기능이 다양하면서도, 변경이 필요한 경우에 클래스를 변경하지 않고, 재사용할 때 유용하게 사용된다.  

어떻게 보면 객체 간의 **의존관계를 제거할 수 있는 패턴**이라고 볼 수 있다.  

말로는 어렵다...  

직접 구현해보면서 **커맨드 패턴**을 이해해보자.  

<br>

## 요구사항: 우리집에 `Siri`를 설치하기  

당신은 당신만의 `Siri`를 집에 설치하기로 했다.  

당신은 Siri에게 **2 종류의 명령**을 내릴 수 있다.  

- `order`
    - 예) 밥솥 켜
- `undo`
    - 예) 밥솥 꺼  

우선, 당신이 명령할 수 있는 것은 밥통의 전원을 `ON/OFF` 할 수 밖에 없다.  

<br>

## 클래스 분리  

- `RiceCooker Class`
  - void powerOn() : 밥솥 전원 ON
  - void powerOff() : 밥솥 전원 OFF
- `Siri Class`
  - void order() : 명령하기
  - void undo() : 명령 취소하기
- `Client Class`
  - void main()  
 
<br>

## 구현하기  

```
public class Siri {
    private RiceCooker riceCooker;

    public void setRiceCooker(RiceCooker riceCooker) {
        this.riceCooker = riceCooker;
    }

    public void run() {
        riceCooker.powerOn();
    }

    public void undo() {
        riceCooker.powerOff();
    }
}
```

```
public class RiceCooker {
    private boolean isOn;

    public void powerOn() {
        this.isOn = true;
        System.out.println("밥솥 전원이 켜졌습니다.");
    }

    public void powerOff() {
        this.isOn = false;
        System.out.println("밥솥 전원이 꺼졌습니다.");
    }
}
```  

```
public class Client {
    public static void main(String[] args) {
        RiceCooker riceCooker = new RiceCooker();

        Siri siri = new Siri();
        siri.setRiceCooker(riceCooker);

        siri.run();

        siri.undo();
    }
}
```  

간단하게 구현해봤다. 이제 **엘레베이터를 호출**할 수 있는 기능을 구매했다고 하자.  

<br>

## 새로운 기능의 추가

- `Elevator Class`
  - call() : 호출하기
  - cancelCall() : 호출 취소하기

위 추가된 기능을 구현해보자.  

![패턴 전](https://github.com/hbkuk/blog/assets/109803585/e1b9f7f5-f9d7-4fa6-93a8-c2c69f3f3b24)

```
public class Siri {
    private RiceCooker riceCooker;
    private Elevator elevator;

    public void setRiceCooker(RiceCooker riceCooker) {
        this.riceCooker = riceCooker;
    }

    public void setElevator(Elevator elevator) {
        this.elevator = elevator;
    }

    public void riceCookerPowerOn() {
        riceCooker.powerOn();
    }

    public void riceCookerPowerOff() {
        riceCooker.powerOff();
    }

    public void elevatorCall() {
        elevator.call();
    }

    public void elevatorCallCancel() {
        elevator.callCancel();
    }
}
```  

```
public class RiceCooker {
    private boolean isOn;

    public void powerOn() {
        this.isOn = true;
        System.out.println("밥솥 전원이 켜졌습니다.");
    }

    public void powerOff() {
        this.isOn = false;
        System.out.println("밥솥 전원이 꺼졌습니다.");
    }
```  

```
public class Elevator {
    private boolean isCall;

    public void call() {
        this.isCall = true;
        System.out.println("엘레베이터를 호출했습니다.");
    }

    public void callCancel() {
        this.isCall = false;
        System.out.println("엘레베이터를 호출을 실패했습니다.");
    }
}
```  

```
public class Client {
    public static void main(String[] args) {
        Siri siri = new Siri();
        
        RiceCooker riceCooker = new RiceCooker();

        siri.setRiceCooker(riceCooker);
        siri.riceCookerPowerOn();
        siri.riceCookerPowerOff();

        Elevator elevator = new Elevator();

        siri.setElevator(elevator);
        siri.elevatorCall();
        siri.elevatorCallCancel();
    }
}
```


코드가 굉장히 더러워졌다..  

`Siri`의 기능이 **많아질 수록 필드도 늘어나고, 메서드도 늘어나고, 관리하기도 굉장히 어려워진다.**  

우리는 이럴때 `커맨드 패턴`을 적용할 수 있다.  

<br>

## 커맨드 패턴 적용  

![패턴 후](https://github.com/hbkuk/blog/assets/109803585/fbca7ab8-c27c-4899-96b7-9726755d2af8)  

Command 인터페이스를 선언했다.  

이제 `siri`는 **Command 인터페이스를 구현한 객체(RiceCooker, Elevator 등..)가 누군지 모른다. 그냥 작동시킬 뿐이다.**  

<br>

이로써 이전에 존재했던 의존 관계

즉, **Siri와 각 기능들과의 관계가 사라진 것을 확인**할 수 있다.  

변경된 부분의 소스코드이다.  

```
public class Siri {
    private Command command;

    public void setCommand(Command command) {
        this.command = command;
    }

    public void order() {
        if( this.command != null ) {
            command.order();
            System.out.println(System.lineSeparator());
        }
    }

    public void undo() {
        if( this.command != null ) {
            command.undo();
            System.out.println(System.lineSeparator());
        }
    }
}
```

```
public class ElevatorCommand implements Command {
    private Elevator elevator;

    public ElevatorCommand(Elevator elevator) {
        this.elevator = elevator;
    }

    @Override
    public void order() {
        elevator.call();
    }

    @Override
    public void undo() {
        elevator.callCancel();
    }
}
```

```
public class RiceCookerCommand implements Command {
    private RiceCooker riceCooker;

    public RiceCookerCommand(RiceCooker riceCooker) {
        this.riceCooker = riceCooker;
    }

    @Override
    public void order() {
        riceCooker.powerOn();
    }

    @Override
    public void undo() {
        riceCooker.powerOff();
    }
}
```
```
public class Client {
    public static void main(String[] args) {
        RiceCooker riceCooker = new RiceCooker();
        Elevator elevator = new Elevator();

        Command riceCookerCommand = new RiceCookerCommand(riceCooker);
        Command elevatorCommand = new ElevatorCommand(elevator);

        Siri siri = new Siri();

        siri.setCommand(riceCookerCommand);
        siri.order();
        siri.undo();

        siri.setCommand(elevatorCommand);
        siri.order();
        siri.undo();
    }
}
```  

끝으로,  

위 구현에서 한단계 나아가려면, `redo()` 기능을 구현하는 것이다.  

이는 Java에서 제공하는 Stack API를 활용해서 구현할 수 있다.  

</div>