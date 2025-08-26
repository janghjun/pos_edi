import { useEffect, useState } from 'react'

export default function POList(){
  const [rows,setRows] = useState([])
  const load = async()=>{
    const r = await fetch('http://localhost:8000/po/list')
    setRows(await r.json())
  }
  useEffect(()=>{ load() },[])
  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">본사 — 발주(PO)</h1>
      <button className="px-3 py-2 border rounded mb-3" onClick={load}>새로고침</button>
      <table className="w-full border">
        <thead><tr><th>PO No</th><th>Supplier</th><th>Store</th><th>Status</th><th>ETA</th><th>Created</th></tr></thead>
        <tbody>
        {rows.map((r,i)=> (
          <tr key={i}>
            <td>{r.po_no}</td>
            <td>{r.supplier_id}</td>
            <td>{r.store_id}</td>
            <td>{r.status}</td>
            <td>{r.expected_date}</td>
            <td>{r.created_at}</td>
          </tr>
        ))}
        </tbody>
      </table>
    </div>
  )
}
