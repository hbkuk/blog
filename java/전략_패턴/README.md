# RPG 게임에서의 캐릭터 구현

초기 요구사항은 다음과 같다.  

<br>

## 전사의 등장

무기로 `Sword(검)`을 가진 **전사**(Warrior)가 존재하며, `attack()`을 사용해서 **공격**할 수 있다.

그렇다면, 다음과 같이 클래스를 생성할 수 있을 것이다.

- SwordWarrior Class
  - void attack()

```
public class SwordWarrior {

    public void name() {
        System.out.println("전사입니다.");
    }

    public void attack() {
        System.out.println("검을 휘둘러 공격합니다.");
    }
}
```

```
public class Application {
    public static void main(String[] args) {
        SwordWarrior swordWarrior = new SwordWarrior();

        swordWarrior.attack();
    }
}
```  

<br>  

## 궁수의 등장

운영을 하다보니, 요구사항이 추가되었다.  

<br>

그것은, `궁수(Archer)`라는 **직업을 추가**하는 것이다.

무기로 `Bow`를 가진 **궁수**(Archer)가 존재하며, `attack()`을 사용해서 공격할 수 있다.

그렇다면, 다음과 같이 클래스를 생성할 수 있을 것이다.

- Archer Class
  - void attack()

```
public class BowArcher {
    public void name() {
        System.out.println("궁수입니다.");
    }

    public void attack() {
        System.out.println("활을 쏴서 공격합니다.");
    }
}
```

```
public class Application {
    public static void main(String[] args) {
        SwordWarrior swordWarrior = new SwordWarrior();
        BowArcher bowArcher = new BowArcher();

        swordWarrior.attack();
        bowArcher.attack();
    }
}
```  

<br>  


이러한 직업들이 계속해서 추가한다고 생각해보자.  

![추가](https://github.com/hbkuk/blog/assets/109803585/f04ba1a7-ed99-4156-a1df-d0313c67b485)

<br>

각 직업마다 공통 부분이 보이는가?  

<br>

(해당 내용에서는 `name()` 메서드는 중요한 부분이 아니기에 제외하도록 한다)

공통부분은 각 직업마다 가지고 있는 `attack()` 메서드이다.  

이를 **추상 메서드**로 선언해보자.  

![추가](https://github.com/hbkuk/blog/assets/109803585/64cce5d3-2a09-4d86-b710-3280ca3f422f)

```
public abstract class Character {

    abstract void attack();

}
```  

각 직업은 이를 상속받도록 하고, 추상 메서드를 구현해보자.  

```
public class SwordWarrior extends Character {
    public void attack() {
        System.out.println("검을 휘둘러 공격합니다.");
    }
}
```

```
public class BowArcher extends Character {
    public void attack() {
        System.out.println("활을 쏴서 공격합니다.");
    }
}
```

```
public class WandWizard extends Character {
    public void attack() {
        System.out.println("지팡이로 주문을 사용해 공격합니다.");
    }
}
```

```
public class Application {
    public static void main(String[] args) {
        Character character = new WandWizard();
        character.attack();
    }
}
```  

<br>  

## 직업마다 고유한 스킬을 추가  

운영을 하다보니, 이제는 직업마다 고유한 스킬을 사용할 수 있도록 제공하고자 한다.  

어떻게 해야할까?  

```
public abstract class Character {
    abstract void attack();
    abstract void ultimate();
}
```   

추상 클래스에서 추상 메서드 `ultimate()`를 추가했다.  

<br>

하지만, 

현재까지 도끼나 창 등의 무기를 가진 다양한 전사 직업이 추가되어서 총 **100개**가 넘었다고 생각해보자.  

모든 하위 클래스에서 해당 기능을 추가해줘야 한다.  

<br>

또, 다른 상황을 생각해보자.  

<br>  

모든 하위 클래스에 `ultimate()`를 구현했는데,

`ultimate()`를 수정해야하는 상황이 온다면 어떻게될까?  

모든 클래스 전부 다 수정해야한다.  

```  
@Override
void ultimate() {
    System.out.println("일정시간동안 공격력이 증가합니다.");
}
```  

상상만 해도 끔찍하다.  

<br>

또한, 이러한 상황에서 **또, 또, 또, 또**  

새로운 기능이 추가된다고 생각해보자..  

예를 들면, 각 직업마다 서브 스킬이 추가된다고 했을때, 추상 클래스에는 `subSkillA()`이 추가되지만, 

이를 상속받는 클래스들에 전부 다 추가해줘야하는 상황이 발생한다.  

*저 그만하고싶어요..* 라는말이 나오지 않을까?  

<br>

우리는 이러한 상황을 해결하기 위해 **전략패턴**을 사용하면 된다.  

각각의 기능을 하나의 전략으로 **그룹화** 시키는 것이다. 

![전략패턴](https://github.com/hbkuk/blog/assets/109803585/5a534118-8f63-4dd8-bfa5-e28657ea0796)


```
public class Character {

    private AttackStrategy attackStrategy;
    private UltimateStrategy ultimateStrategy;

    public Character(AttackStrategy attackStrategy,
                     UltimateStrategy ultimateStrategy) {
        this.attackStrategy = attackStrategy;
        this.ultimateStrategy = ultimateStrategy;
    }

    public void attack() {
        attackStrategy.attack();
    }

    public void ultimate() {
        ultimateStrategy.ultimate();
    };

}
```

```
public interface AttackStrategy {
    void attack();
}
```

```
public interface UltimateStrategy {
    void ultimate();
}
```

```
public class SwordWarrior implements AttackStrategy {

    @Override
    public void attack() {
        System.out.println("검을 휘둘러 공격합니다.");
    }

}
```

```
public class ShieldDefense implements UltimateStrategy {
    @Override
    public void ultimate() {
        System.out.println("일정시간동안 방어력을 1.5배 증가시킵니다.");
    }
}
```  

```
public class Application {
    public static void main(String[] args) {
        Character character = new Character(new SwordWarrior(), new ShieldDefense());

        character.attack();
        character.ultimate();
    }
}
```

이렇게 구현하면, **메서드 수정**도 간편하다.  

<br>

현재, `ShieldDefense`의 기능은 일정시간동안 방어력을 1.5배 증가시킨다.   

1.6배로 변경해보자.  

```
public class ShieldDefense implements UltimateStrategy {
    @Override
    public void ultimate() {
        System.out.println("일정시간동안 방어력을 1.6배 증가시킵니다.");
    }
}
```  

간단하게 수정이 가능하다.  

새로운 기능이 추가된다고 했을 때, **새로운 전략을 추가**해주면 된다.  

```
public class Character {
    private AttackStrategy attackStrategy;
    private UltimateStrategy ultimateStrategy;
    private MoveStrategy moveStrategy; 

    ... 코드 추가
}
```