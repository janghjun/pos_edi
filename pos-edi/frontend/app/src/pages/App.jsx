import React, { useState } from 'react'
import SaleForm from '../shared/SaleForm.jsx'
import POList from '../shared/POList.jsx'

export default function App(){
  const [tab,setTab] = useState('pos')
  const btn = (id, label)=> (
    <button onClick={()=>setTab(id)} style={{padding:'8px 12px', marginRight:8, borderRadius:8, border: '1px solid #ddd', background: tab===id?'#111':'#fff', color: tab===id?'#fff':'#111'}}>
      {label}
    </button>
  )
  return (
    <div style={{padding:16, fontFamily:'system-ui, -apple-system, Segoe UI, Roboto, Noto Sans KR, sans-serif'}}>
      <h1 style={{fontSize:24, fontWeight:700, marginBottom:12}}>POS ↔ HQ ↔ Supplier EDI Console</h1>
      <div style={{marginBottom:12}}>
        {btn('pos','POS 판매 입력')}
        {btn('po','본사 PO 목록')}
      </div>
      <div style={{border:'1px solid #eee', borderRadius:12, padding:16}}>
        {tab==='pos' ? <SaleForm/> : <POList/>}
      </div>
      <p style={{opacity:.6, marginTop:12}}>HQ API: :8000 · POS API: :8001</p>
    </div>
  )
}
