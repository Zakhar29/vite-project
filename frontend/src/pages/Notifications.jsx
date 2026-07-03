import "../styles/notifications.css";

function Notifications() {

const notifications = [
{
id:1,
text:"Новый комментарий под твоим треком",
time:"2 минуты назад"
},
{
id:2,
text:"Новый комментарий под твоим треком",
time:"2 минуты назад"
},
{
id:3,
text:"Новый комментарий под твоим треком",
time:"2 минуты назад"
},
{
id:4,
text:"Новый комментарий под твоим треком",
time:"2 минуты назад"
},
{
id:5,
text:"Новый комментарий под твоим треком",
time:"2 минуты назад"
},
];

return (
<div className="notifications-page">
<div className="notifications-page__inner">

<div className="notifications-header">

<h1>Уведомления</h1>

<button className="read-all">
Пометить все прочитанными
</button>

</div>

<div className="notifications-list">

{notifications.map((n,index)=>(
<div className="notification-card" key={n.id}>

<div className="notification-left">

<div className="icon">💬</div>

<p>{n.text}</p>

</div>

<div className="notification-right">

<span>{n.time}</span>

{index === notifications.length - 1 && (
<button className="read-one">
Пометить как прочитанное
</button>
)}

</div>

</div>
))}

</div>

</div>

</div>
);

}

export default Notifications;