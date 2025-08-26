import { useState } from 'react'

export default function SaleForm(){
  const [items,setItems] = useState([{sku:'A001', qty:1, unit_price:45000, discount:0}])
  const [result,setResult] = useState(null)

  const addRow = ()=> setItems([...items,{sku:'',qty:1,unit_price:0,discount:0}])
  const onChange = (i, key, val)=>{
    const next = [...items]; next[i][key] = ['qty','unit_price','discount'].includes(key)? Number(val): val; setItems(next)
  }
  const submit = async()=>{
    const payload = { store_id:'ST001', pos_txn_id:`TXN-${Date.now()}`, items, payment:{method:'CARD', amount: items.reduce((s,x)=>s+x.qty*x.unit_price-x.discount,0)} }
    const r = await fetch('http://localhost:8001/sales',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    setResult(await r.json())
  }
  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">POS — 판매</h1>
      <table className="w-full border mb-4">
        <thead><tr><th>SKU</th><th>QTY</th><th>PRICE</th><th>DC</th></tr></thead>
        <tbody>
          {items.map((it,i)=> (
            <tr key={i}>
              <td><input className="border p-1 w-full" value={it.sku} onChange={e=>onChange(i,'sku',e.target.value)} /></td>
              <td><input className="border p-1 w-20" type="number" value={it.qty} onChange={e=>onChange(i,'qty',e.target.value)} /></td>
              <td><input className="border p-1 w-28" type="number" value={it.unit_price} onChange={e=>onChange(i,'unit_price',e.target.value)} /></td>
              <td><input className="border p-1 w-20" type="number" value={it.discount} onChange={e=>onChange(i,'discount',e.target.value)} /></td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex gap-2">
        <button className="px-3 py-2 border rounded" onClick={addRow}>+ 줄 추가</button>
        <button className="px-3 py-2 bg-black text-white rounded" onClick={submit}>결제(Enter)</button>
      </div>
      {result && (
        <pre className="mt-4 bg-gray-100 p-3 rounded text-sm">{JSON.stringify(result,null,2)}</pre>
      )}
    </div>
  )
}
