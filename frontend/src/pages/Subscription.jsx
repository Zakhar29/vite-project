import { useState } from "react";
import "../styles/subscription.css";

function Subscription() {

const [method, setMethod] = useState("card");

return (

<div className="subscription-page">

<div className="subscription-container">

<h1>Оформление подписки</h1>

<p className="subtitle">
Выберите способ оплаты и введите данные
</p>

{/* СПОСОБЫ ОПЛАТЫ */}

<div className="payment-methods">

<div
className={`method ${method==="card" ? "active" : ""}`}
onClick={()=>setMethod("card")}
>
💳
<p>Карта</p>
</div>

<div
className={`method ${method==="paypal" ? "active" : ""}`}
onClick={()=>setMethod("paypal")}
>
✔
<p>PayPal</p>
</div>

<div
className={`method ${method==="qiwi" ? "active" : ""}`}
onClick={()=>setMethod("qiwi")}
>
💰
<p>QIWI</p>
</div>

</div>

{/* ФОРМА КАРТЫ */}

{method==="card" && (

<div className="card-form">

<label>Номер карты</label>
<input placeholder="**** **** **** ****"/>

<div className="card-row">

<div>
<label>Срок действия</label>
<input placeholder="MM/YY"/>
</div>

<div>
<label>CVC</label>
<input placeholder="***"/>
</div>

</div>

</div>

)}

<div className="subscription-footer">

<div className="total">
<span>Итого:</span>
<b>249.00 ₽</b>
</div>

<div className="buttons">

<button className="cancel">
Отмена
</button>

<button className="pay">
Оплатить
</button>

</div>

</div>

</div>

</div>

);

}

export default Subscription;