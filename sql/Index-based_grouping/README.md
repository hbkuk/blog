## GROUP BY 절의 인덱스 사용
---
SQL에서 `GROUP BY`가 사용된다면, 인덱스의 사용 여부는 어떻게 결정될까?  

`GROUP BY` 절에 명시된 칼럼의 순서가 인덱스를 구성하는 칼럼의 순서와 같으면 `GROUP BY` 절은 일단 인덱스를 사용할 수 있다.  

아래 예는 여러개의 칼럼으로 구성된 다중 칼럼 인덱스를 기준으로 한다.  

- `GROUP BY` **절에 명시된 칼럼이 인덱스 칼럼의 순서**와 위치가 같아야한다.
- 인덱스를 구성하는 칼럼 중에서 뒤쪽에 있는 칼럼은 `GROUP BY` 절에 명시되지 않아도 인덱스를 사용 할 수 있지만, 인덱스의 앞쪽에 있는 칼럼이 `GROUP BY` 절에 명시되지 않으면 인덱스를 사용할 수 없다.
- WHERE 조건절과는 달리 `GROUP BY` 절에 **명시된 칼럼이 하나라도 인덱스에 없으면** `GROUP BY` 절은 전혀 **인덱스를 이용하지 못한다.**  

> ### GROUP BY 절에 명시된 칼럼이 인덱스 칼럼의 순서와 위치가 같아야한다.  

아래와 같은 orders 테이블이 있다고 가정한다.  

- Column 구성: (주문번호) order_id, (고객번호) customer_id, (주문일자) order_date, (상품번호) product_id, (수량) quantity 
- index 구성 및 순서 : (customer_id, order_date, product_id)  

```
CREATE INDEX idx_orders_customer_date_product ON orders (customer_id, order_date, product_id);
```  

이러한 상황에서 특정 시간 범위에서 각 고객이 주문한 각 제품의 총 수량(quantity)을 고객 번호(customer_id) 및 주문일자(order_date) 별로 정렬 후 검색하려면 다음과 같은 쿼리를 작성할 수 있다.  

```
SELECT customer_id, order_date, product_id, SUM(quantity)
FROM orders
WHERE order_date BETWEEN '2022-01-01' AND '2022-12-31'
GROUP BY customer_id, order_date, product_id
ORDER BY customer_id, order_date;
```  

이 쿼리는 다음과 같은 절차로 진행된다.
- WHERE 절에서 order_date 칼럼으로 **필터링**
- GROUP BY 절을 사용해서 customer_id, order_date, product_id 칼럼으로 행을 **그룹화**
- SUM 함수를 사용해서 각 그룹에 대한 quantity 칼럼의 합을 **계산**
- 결과 집합을 customer_id, order_date로 **정렬**  

인덱스는 customer_id, order_date, product_id) 컬럼에 생성되었으며, GROUP BY 절의 컬럼 순서와 인덱스 컬럼이 동일한 순서이므로, 인덱스를 활용할 수 있다.  

만약, GROUP BY 절의 칼럼 순서를 order_date, customer_id, product_id로 변경한다면?  

```
SELECT order_date, customer_id, product_id, SUM(quantity)
FROM orders
WHERE order_date BETWEEN '2022-01-01' AND '2022-12-31'
GROUP BY order_date, customer_id, product_id
ORDER BY customer_id, order_date;
```  

GROUP BY 절의 컬럼 순서와 인덱스 컬럼에 순서가 일치하지 않아므로, 인덱스를 활용할 수 있다.  

> ### 인덱스를 구성하는 칼럼 중에서 뒤쪽에 있는 칼럼은 `GROUP BY` 절에 명시되지 않아도 인덱스를 사용 할 수 있지만, 인덱스의 앞쪽에 있는 칼럼이 `GROUP BY` 절에 명시되지 않으면 인덱스를 사용할 수 없다.  

특정 시간에서 고객당 총 수량을 검색하려면 다음과 같은 쿼리를 작성할 수 있다.  

```
SELECT customer_id, SUM(quantity)
FROM orders
WHERE order_date BETWEEN '2022-01-01' AND '2022-12-31'
GROUP BY customer_id;
```  

이 쿼리는 다음과 같은 절차로 진행된다.
- WHERE 절에서 order_date 칼럼으로 필터링
- GROUP BY 절을 사용해서 customer_id 칼럼으로 행을 그룹화
- SUM 함수를 사용해서 합계를 계산  

인덱스는 (customer_id, order_date, product_id) 칼럼에 생성되므로, product_id 칼럼이 GROUP BY 절이나 포함되지 않아도 옵티마이저는 인덱스를 사용해서 그룹화 작업을 최적화할 수 있다.  

customer_id 칼럼이 인덱스에서 가장 왼쪽 열이고, 인덱스가 customer_id를 기준으로 먼저 정렬되었기 때문에 가능하다.  

> ### WHERE 조건절과는 달리 `GROUP BY` 절에 **명시된 칼럼이 하나라도 인덱스에 없으면** `GROUP BY` 절은 전혀 **인덱스를 이용하지 못한다.**  

특정 시간 범위에서 특정 시간에서 특정 고객이 주문한 각 제품의 총 수량을 검색하려면 다음과 같은 쿼리를 작성할 수 있다.  
  
```
SELECT product_id, SUM(quantity)
FROM orders
WHERE customer_id = 123 AND order_date BETWEEN '2022-01-01' AND '2022-12-31'
GROUP BY product_id;
```  

이 쿼리는 다음과 같은 절차로 진행된다.
- WHERE 절에서 customer_id 및 order_date 칼럼으로 필터링
- GROUP BY 절을 사용해 product_id 열로 나머지 행을 그룹화
- SUM 함수를 사용해서 각 그룹에 대한 quantity 칼럼의 합계를 계산  
  
customer_id 및 order_date 칼럼이 인덱싱된 경우 옵티마이저는 인덱스를 활용해서 최적화 할 수 있다.  
  
반면, product_id 칼럼이 인덱싱되지 않은 경우, 인덱스를 사용할 수 없다.