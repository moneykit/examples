var f=Object.defineProperty,g=Object.defineProperties;var h=Object.getOwnPropertyDescriptors;var d=Object.getOwnPropertySymbols;var i=Object.prototype.hasOwnProperty,j=Object.prototype.propertyIsEnumerable;var e=(c,a,b)=>a in c?f(c,a,{enumerable:!0,configurable:!0,writable:!0,value:b}):c[a]=b,k=(c,a)=>{for(var b in a||(a={}))i.call(a,b)&&e(c,b,a[b]);if(d)for(var b of d(a))j.call(a,b)&&e(c,b,a[b]);return c},l=(c,a)=>g(c,h(a));var m=(c,a)=>{for(var b in a)f(c,b,{get:a[b],enumerable:!0})};export{k as a,l as b,m as c};