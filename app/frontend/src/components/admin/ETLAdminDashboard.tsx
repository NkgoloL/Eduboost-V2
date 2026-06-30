// @ts-nocheck
"use client";

import { useState, useEffect, useMemo, useRef, useCallback } from "react";

// ── Constants ──────────────────────────────────────────────────────────────
const STATUS_META = {
  raw:               { label:"Raw",           color:"#64748b", bg:"rgba(100,116,139,.12)" },
  acquired:          { label:"Acquired",       color:"#38bdf8", bg:"rgba(56,189,248,.12)" },
  extracted:         { label:"Extracted",      color:"#818cf8", bg:"rgba(129,140,248,.12)" },
  normalized:        { label:"Normalized",     color:"#a78bfa", bg:"rgba(167,139,250,.12)" },
  metadata_enriched: { label:"Enriched",       color:"#c084fc", bg:"rgba(192,132,252,.12)" },
  chunked:           { label:"Chunked",        color:"#e879f9", bg:"rgba(232,121,249,.12)" },
  validated:         { label:"Validated",      color:"#34d399", bg:"rgba(52,211,153,.12)" },
  needs_review:      { label:"Needs Review",   color:"#fbbf24", bg:"rgba(251,191,36,.12)" },
  approved:          { label:"Approved",       color:"#22c55e", bg:"rgba(34,197,94,.12)" },
  indexed:           { label:"Indexed",        color:"#06b6d4", bg:"rgba(6,182,212,.12)" },
  training_ready:    { label:"Training Ready", color:"#10b981", bg:"rgba(16,185,129,.12)" },
  rejected:          { label:"Rejected",       color:"#f87171", bg:"rgba(248,113,113,.12)" },
  archived:          { label:"Archived",       color:"#9ca3af", bg:"rgba(156,163,175,.12)" },
};
const SUBJECTS  = ["mathematics","english","science","history","geography","accounting","economics","life_sciences","physical_sciences"];
const DOC_TYPES = ["textbook","workbook","teacher_guide","lesson_plan","assessment_rubric","past_paper","memorandum","curriculum_statement","act_regulation","worksheet","study_material","remediation","enrichment"];
const GRADES    = Array.from({length:12},(_,i)=>i+1);
const PHASES    = ["Foundation Phase","Intermediate Phase","Senior Phase","FET Phase"];
const TABS = [
  ["overview","Overview"],["documents","Documents"],["gaps","Coverage"],
  ["review","Review"],["search","Search"],["training","Training"],
  ["monitoring","Monitoring"],["jobs","Jobs"],
];
const FEEDBACK_TYPES = ["incorrect_answer","missing_document","outdated_document","bad_citation","wrong_grade_subject"];
const RESOLUTION_TYPES = ["fixed","acknowledged","wont_fix","duplicate"];

// ── Seed ───────────────────────────────────────────────────────────────────
function seedData() {
  const authors    = ["DBE Content Team","Lerato Dlamini","Sara van Rensburg","Amara Osei","Thabo Nkosi","Pieter de Jager"];
  const publishers = ["Macmillan","Oxford SA","Shuter & Shooter","Vivlia","Pearson SA","DBE"];
  const issues     = [
    "Incomplete metadata: 2/4 required fields missing",
    "License status unknown — cannot approve for training use",
    "Very few chunks produced — document may be truncated",
    "No headings detected — structure extraction failed",
    "Duplicate chunks detected in pages 14-20",
    "Low OCR confidence (0.42) on pages 3–7",
    "Subject and grade not detected — manual review required",
  ];
  const statuses = Object.keys(STATUS_META);
  const docs = [];
  let id = 1000;
  for (let g=1;g<=12;g++){
    const subjSlice = SUBJECTS.slice(0,g<4?3:g<7?5:8);
    for (const subj of subjSlice){
      const count = Math.floor(Math.random()*4)+1;
      for (let k=0;k<count;k++){
        const dtype  = DOC_TYPES[Math.floor(Math.random()*DOC_TYPES.length)];
        const status = statuses[Math.floor(Math.random()*statuses.length)];
        const qs = status==="approved"||status==="training_ready"?0.72+Math.random()*.28
                 : status==="rejected"?Math.random()*.39
                 : status==="needs_review"?0.4+Math.random()*.3:0.3+Math.random()*.6;
        docs.push({
          document_id:`doc-${++id}`, title:`Grade ${g} ${subj.replace(/_/g," ")} ${dtype.replace(/_/g," ")} ${k+1}`.replace(/\b\w/g,c=>c.toUpperCase()),
          document_type:dtype,subject:subj,grade:g,phase:g<=3?PHASES[0]:g<=6?PHASES[1]:g<=9?PHASES[2]:PHASES[3],
          language:Math.random()>.85?"af":"en",processing_status:status,quality_score:+qs.toFixed(3),
          training_readiness:status==="training_ready"||(status==="approved"&&qs>.8),
          license_status:Math.random()>.3?"government_open":Math.random()>.5?"open_license":"unknown",
          publisher:publishers[Math.floor(Math.random()*publishers.length)],
          author:authors[Math.floor(Math.random()*authors.length)],
          publication_year:2018+Math.floor(Math.random()*7),
          page_count:Math.floor(Math.random()*200)+10,
          file_size_bytes:Math.floor(Math.random()*8000000)+100000,
          chunk_count:Math.floor(Math.random()*120)+5,
          curriculum:"CAPS",
          created_at:new Date(Date.now()-Math.random()*1e10).toISOString(),
          updated_at:new Date(Date.now()-Math.random()*1e9).toISOString(),
          reviewer_notes:(status==="needs_review"||status==="rejected")?issues[Math.floor(Math.random()*issues.length)]:null,
        });
      }
    }
  }
  const reviewTasks = docs.filter(d=>d.processing_status==="needs_review").map((d,i)=>({
    task_id:`task-${i}`,document_id:d.document_id,title:d.title,grade:d.grade,
    subject:d.subject,document_type:d.document_type,
    reason:issues[Math.floor(Math.random()*issues.length)],
    quality_score:d.quality_score,created_at:d.updated_at,
    priority:["high","normal","normal","low"][Math.floor(Math.random()*4)],
    assigned_to:Math.random()>.5?authors[Math.floor(Math.random()*authors.length)]:null,
  }));
  const stats={};
  for (const s of Object.keys(STATUS_META)) stats[s]=docs.filter(d=>d.processing_status===s).length;
  stats.total=docs.length;
  stats.avg_quality_score=+(docs.reduce((a,d)=>a+d.quality_score,0)/docs.length).toFixed(3);
  stats.pending_reviews=reviewTasks.length;
  stats.training_ready_count=docs.filter(d=>d.training_readiness).length;
  stats.indexed_count=docs.filter(d=>["indexed","training_ready"].includes(d.processing_status)).length;
  const stages=["ingest","extract","normalize","chunk","validate","index","embed"];
  const jStatuses=["success","success","success","success","failed","running"];
  const jobs=Array.from({length:40},(_,i)=>({
    job_id:`job-${i}`,document_id:docs[Math.floor(Math.random()*docs.length)].document_id,
    stage:stages[Math.floor(Math.random()*stages.length)],
    status:jStatuses[Math.floor(Math.random()*jStatuses.length)],
    started_at:new Date(Date.now()-Math.random()*3600000).toISOString(),
    finished_at:new Date(Date.now()-Math.random()*1800000).toISOString(),error:null,
  }));
  const dsTypes=["qa","summary","concept","rubric"];
  const datasets=dsTypes.map((t,i)=>({
    dataset_id:`ds-${i+1}`,name:`${t.toUpperCase()} Training Set v1`,
    dataset_type:t,version:"1.0",split:"train",
    example_count:200+Math.floor(Math.random()*800),
    is_synthetic:1,created_at:new Date(Date.now()-Math.random()*5e8).toISOString(),
    export_path:i<2?`./exports/dataset_ds-${i+1}_20250520.jsonl`:null,
    human_reviewed_pct:Math.floor(Math.random()*60)+10,
    avg_quality:+(0.6+Math.random()*.35).toFixed(2),
    grade_dist:Object.fromEntries(GRADES.slice(0,6).map(g=>[g,Math.floor(Math.random()*80)+10])),
    subject_dist:Object.fromEntries(SUBJECTS.slice(0,5).map(s=>[s,Math.floor(Math.random()*100)+20])),
  }));
  const feedbackItems=Array.from({length:28},(_,i)=>({
    feedback_id:`fb-${i}`,
    feedback_type:FEEDBACK_TYPES[Math.floor(Math.random()*FEEDBACK_TYPES.length)],
    user_id:`user-${100+Math.floor(Math.random()*50)}`,
    document_id:docs[Math.floor(Math.random()*docs.length)].document_id,
    details:["The answer to Q3 is incorrect","Document appears to be from 2015","Citation page doesn't match","Grade listed as 9 but content is grade 11"][Math.floor(Math.random()*4)],
    resolved:Math.random()>.6?1:0,
    created_at:new Date(Date.now()-Math.random()*7*24*3600000).toISOString(),
    resolved_by:Math.random()>.5?authors[Math.floor(Math.random()*authors.length)]:null,
  }));
  const feedbackCounts=Object.fromEntries(FEEDBACK_TYPES.map(t=>[t,feedbackItems.filter(f=>f.feedback_type===t).length]));
  const metricSeries=Array.from({length:24},(_,i)=>({
    hour:i,
    ingestion:Math.floor(Math.random()*12)+1,
    failures:Math.floor(Math.random()*3),
    approvals:Math.floor(Math.random()*8)+1,
  }));
  const searchResults=docs.filter(d=>["approved","indexed","training_ready"].includes(d.processing_status)).slice(0,10).map(d=>({
    chunk_id:`chunk-${d.document_id}`,document_id:d.document_id,
    heading:`Introduction to ${d.subject?.replace(/_/g," ")||"the topic"}`,
    content_preview:`Core concepts for Grade ${d.grade} ${d.subject?.replace(/_/g," ")}. Learning objectives include understanding foundational principles and applying them to practical problems relevant to the South African CAPS curriculum.`,
    title:d.title,grade:d.grade,subject:d.subject,score:+(0.7+Math.random()*.3).toFixed(2),
    citation:{document_id:d.document_id,title:d.title,section_path:"Chapter 1 > Section 1.1",page_start:1,page_end:4},
  }));
  const monitoring={
    generated_at:new Date().toISOString(),total_documents:stats.total,
    ingestion_rate_7d:14+Math.floor(Math.random()*20),approval_rate:0.72,
    avg_quality_score:stats.avg_quality_score,failed_jobs_24h:jobs.filter(j=>j.status==="failed").length,
    extraction_failure_rate:0.08,feedback_summary:feedbackCounts,
    stale_documents:docs.filter(d=>["acquired","extracted","normalized"].includes(d.processing_status)).slice(0,8).map(d=>({...d,days_stale:Math.floor(Math.random()*120)+10})),
    alerts:[`${stats.pending_reviews} documents pending human review.`,"Extraction failure rate 8% — check PDF parser for corrupted files.","Grade 10 Physical Sciences has no approved past papers."],
    metric_series:metricSeries,
  };
  return {documents:docs,stats,reviewTasks,jobs,datasets,monitoring,searchResults,feedbackItems};
}
const DATA=seedData();

// ── Primitives ─────────────────────────────────────────────────────────────
const Btn=({children,onClick,variant="ghost",disabled,style:s={}})=>{
  const base={padding:"7px 14px",borderRadius:7,fontSize:12,fontWeight:600,cursor:disabled?"not-allowed":"pointer",transition:"all .15s",border:"1px solid",opacity:disabled ? .45 : 1,...s};
  const v={ghost:{background:"transparent",borderColor:"rgba(255,255,255,.1)",color:"#94a3b8"},
           green:{background:"rgba(34,197,94,.1)",borderColor:"rgba(34,197,94,.3)",color:"#22c55e"},
           red:{background:"rgba(248,113,113,.1)",borderColor:"rgba(248,113,113,.3)",color:"#f87171"},
           blue:{background:"rgba(129,140,248,.1)",borderColor:"rgba(129,140,248,.3)",color:"#818cf8"},
           amber:{background:"rgba(251,191,36,.1)",borderColor:"rgba(251,191,36,.3)",color:"#fbbf24"}};
  return <button onClick={disabled?undefined:onClick} style={{...base,...v[variant]}}>{children}</button>;
};

function StatusBadge({status,size="sm"}){
  const m=STATUS_META[status]||{label:status,color:"#9ca3af",bg:"rgba(156,163,175,.12)"};
  return <span style={{display:"inline-flex",alignItems:"center",gap:4,padding:size==="sm"?"2px 8px":"4px 12px",borderRadius:20,fontSize:size==="sm"?11:12,fontWeight:600,letterSpacing:.03,color:m.color,background:m.bg,border:`1px solid ${m.color}28`,whiteSpace:"nowrap"}}>
    <span style={{width:5,height:5,borderRadius:"50%",background:m.color,flexShrink:0}}/>{m.label}</span>;
}
function QualityBar({score}){
  const pct=Math.round(score*100),color=score>=.7?"#22c55e":score>=.4?"#fbbf24":"#f87171";
  return <div style={{display:"flex",alignItems:"center",gap:8}}>
    <div style={{flex:1,height:4,borderRadius:4,background:"rgba(255,255,255,.08)"}}>
      <div style={{width:`${pct}%`,height:"100%",borderRadius:4,background:color}}/>
    </div>
    <span style={{fontSize:11,color,fontWeight:700,minWidth:28}}>{pct}%</span>
  </div>;
}
function StatCard({label,value,sub,color="#e2e8f0",icon}){
  return <div style={{background:"rgba(255,255,255,.03)",border:"1px solid rgba(255,255,255,.07)",borderRadius:12,padding:"18px 22px",flex:1,minWidth:130}}
    onMouseEnter={e=>e.currentTarget.style.borderColor="rgba(255,255,255,.15)"}
    onMouseLeave={e=>e.currentTarget.style.borderColor="rgba(255,255,255,.07)"}>
    <div style={{fontSize:20,marginBottom:4}}>{icon}</div>
    <div style={{fontSize:28,fontWeight:800,color,lineHeight:1}}>{value}</div>
    <div style={{fontSize:12,color:"#94a3b8",marginTop:4,fontWeight:500}}>{label}</div>
    {sub&&<div style={{fontSize:11,color:"#64748b",marginTop:2}}>{sub}</div>}
  </div>;
}
function Card({title,subtitle,children,style:s={}}){
  return <div style={{background:"rgba(255,255,255,.02)",border:"1px solid rgba(255,255,255,.07)",borderRadius:12,padding:"18px 22px",marginBottom:16,...s}}>
    {title&&<div style={{fontSize:12,fontWeight:700,color:"#64748b",letterSpacing:.08,textTransform:"uppercase",marginBottom:subtitle?3:14}}>{title}</div>}
    {subtitle&&<div style={{fontSize:12,color:"#475569",marginBottom:14}}>{subtitle}</div>}
    {children}
  </div>;
}

// ── SVG Charts ─────────────────────────────────────────────────────────────
function Sparkline({data,color="#818cf8",height=36,width=120}){
  if(!data||!data.length) return null;
  const max=Math.max(...data,1),min=0;
  const pts=data.map((v,i)=>{
    const x=(i/(data.length-1))*width;
    const y=height-((v-min)/(max-min))*(height-4)-2;
    return `${x},${y}`;
  }).join(" ");
  const area=`0,${height} `+pts+` ${width},${height}`;
  return <svg width={width} height={height} style={{overflow:"visible"}}>
    <defs><linearGradient id={`sg-${color.replace("#","")}`} x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stopColor={color} stopOpacity=".3"/>
      <stop offset="100%" stopColor={color} stopOpacity="0"/>
    </linearGradient></defs>
    <polygon points={area} fill={`url(#sg-${color.replace("#","")})`}/>
    <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5"/>
    <circle cx={(data.length-1)/(data.length-1)*width} cy={height-((data[data.length-1]-min)/(max-min))*(height-4)-2} r={3} fill={color}/>
  </svg>;
}
function BarH({label,value,max,color="#818cf8"}){
  const pct=max?Math.round(value/max*100):0;
  return <div style={{marginBottom:6}}>
    <div style={{display:"flex",justifyContent:"space-between",fontSize:11,color:"#94a3b8",marginBottom:3}}>
      <span>{label}</span><span style={{color,fontWeight:700}}>{value}</span>
    </div>
    <div style={{height:5,borderRadius:3,background:"rgba(255,255,255,.06)"}}>
      <div style={{height:"100%",borderRadius:3,background:color,width:`${pct}%`,transition:"width .4s"}}/>
    </div>
  </div>;
}
function DonutChart({data,size=110}){
  const total=data.reduce((a,d)=>a+d.value,0)||1;
  let angle=-Math.PI/2;
  const cx=size/2,cy=size/2,r=40,ir=26;
  const slices=data.map(d=>{const start=angle,span=(d.value/total)*Math.PI*2;angle+=span;return{...d,start,span};});
  const arc=(cx,cy,r,start,span)=>{
    const x1=cx+r*Math.cos(start),y1=cy+r*Math.sin(start);
    const x2=cx+r*Math.cos(start+span),y2=cy+r*Math.sin(start+span);
    return `M${cx},${cy} L${x1},${y1} A${r},${r},0,${span>Math.PI?1:0},1,${x2},${y2} Z`;
  };
  return <svg width={size} height={size}>
    {slices.filter(s=>s.span>.01).map((s,i)=><path key={i} d={arc(cx,cy,r,s.start,s.span)} fill={s.color} opacity={.85}/>)}
    <circle cx={cx} cy={cy} r={ir} fill="#080b14"/>
    <text x={cx} y={cy+5} textAnchor="middle" fontSize={16} fontWeight={800} fill="#e2e8f0">{total}</text>
  </svg>;
}
function MetricChart({series,metric,color,height=60}){
  const vals=series.map(s=>s[metric]);
  return <Sparkline data={vals} color={color} height={height} width={200}/>;
}

// ── Pipeline Flow ──────────────────────────────────────────────────────────
const FLOW=["acquired","extracted","normalized","metadata_enriched","chunked","validated","approved","indexed","training_ready"];
function PipelineFlow({stats}){
  return <div style={{overflowX:"auto",paddingBottom:6}}>
    <div style={{display:"flex",alignItems:"center",minWidth:820}}>
      {FLOW.map((s,i)=>{
        const m=STATUS_META[s],n=stats[s]||0,isLast=i===FLOW.length-1;
        return <div key={s} style={{display:"flex",alignItems:"center",flex:1}}>
          <div style={{flex:1,textAlign:"center",padding:"10px 4px",background:m.bg,border:`1px solid ${m.color}28`,borderRadius:7}}>
            <div style={{fontSize:20,fontWeight:800,color:m.color}}>{n}</div>
            <div style={{fontSize:9,color:m.color,letterSpacing:.06,textTransform:"uppercase",marginTop:2,opacity:.85}}>{m.label}</div>
          </div>
          {!isLast&&<div style={{width:16,flexShrink:0,display:"flex",alignItems:"center",justifyContent:"center"}}>
            <div style={{width:12,height:1,background:"rgba(255,255,255,.1)",position:"relative"}}>
              <div style={{position:"absolute",right:-4,top:-4,color:"rgba(255,255,255,.15)",fontSize:9}}>▶</div>
            </div>
          </div>}
        </div>;
      })}
    </div>
    <div style={{display:"flex",gap:14,marginTop:10,fontSize:11,color:"#94a3b8"}}>
      {["needs_review","rejected","archived"].map(s=><span key={s}>
        <b style={{color:STATUS_META[s].color}}>{stats[s]||0}</b> {STATUS_META[s].label}</span>)}
    </div>
  </div>;
}

// ── Gap Matrix ─────────────────────────────────────────────────────────────
function GapMatrix({documents}){
  const [selType,setSelType]=useState("textbook");
  const matrix=useMemo(()=>{
    const m={};
    for(const g of GRADES){m[g]={};
      for(const s of SUBJECTS){
        const ds=documents.filter(d=>d.grade===g&&d.subject===s&&d.document_type===selType);
        m[g][s]={approved:ds.filter(d=>["approved","training_ready"].includes(d.processing_status)).length,total:ds.length};
      }
    }
    return m;
  },[documents,selType]);
  const bg=(a,t)=>t===0?"rgba(239,68,68,.15)":a===0?"rgba(251,191,36,.12)":"rgba(34,197,94,.12)";
  const bord=(a,t)=>t===0?"rgba(239,68,68,.3)":a===0?"rgba(251,191,36,.25)":"rgba(34,197,94,.25)";
  const txt=(a,t)=>t===0?"#f87171":a===0?"#fbbf24":"#4ade80";
  return <div>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:16}}>
      {DOC_TYPES.slice(0,8).map(dt=><button key={dt} onClick={()=>setSelType(dt)} style={{
        padding:"3px 10px",borderRadius:20,fontSize:10,cursor:"pointer",border:"1px solid",
        background:selType===dt?"rgba(129,140,248,.15)":"transparent",
        borderColor:selType===dt?"rgba(129,140,248,.5)":"rgba(255,255,255,.1)",
        color:selType===dt?"#818cf8":"#475569",fontWeight:600,letterSpacing:.04,textTransform:"capitalize",
      }}>{dt.replace(/_/g," ")}</button>)}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{borderCollapse:"separate",borderSpacing:3,fontSize:11}}>
        <thead><tr><th style={{padding:"4px 8px",color:"#475569",fontWeight:600,textAlign:"left",minWidth:80}}>Grade</th>
          {SUBJECTS.map(s=><th key={s} style={{padding:"4px 6px",color:"#475569",fontWeight:600,textAlign:"center",fontSize:9,textTransform:"uppercase",letterSpacing:.06,maxWidth:70}}>
            {s.replace(/_/g," ")}</th>)}
        </tr></thead>
        <tbody>{GRADES.map(g=><tr key={g}>
          <td style={{padding:"4px 8px",color:"#94a3b8",fontWeight:700,fontSize:12}}>Gr.{g}</td>
          {SUBJECTS.map(s=>{const{approved:a,total:t}=matrix[g]?.[s]||{approved:0,total:0};
            return <td key={s} style={{padding:3}}><div style={{
              width:64,height:28,display:"flex",alignItems:"center",justifyContent:"center",
              borderRadius:5,background:bg(a,t),border:`1px solid ${bord(a,t)}`,
              fontSize:12,fontWeight:700,color:txt(a,t),
            }}>{t===0?"-":`${a}/${t}`}</div></td>;
          })}
        </tr>)}
        </tbody>
      </table>
    </div>
    <div style={{display:"flex",gap:16,marginTop:14,fontSize:11}}>
      {[["rgba(239,68,68,.15)","rgba(239,68,68,.3)","#f87171","No documents"],
        ["rgba(251,191,36,.12)","rgba(251,191,36,.25)","#fbbf24","Exists, none approved"],
        ["rgba(34,197,94,.12)","rgba(34,197,94,.25)","#4ade80","Has approved content"]].map(([bg,bo,c,l])=>
        <div key={l} style={{display:"flex",alignItems:"center",gap:6}}>
          <div style={{width:14,height:14,borderRadius:3,background:bg,border:`1px solid ${bo}`}}/>
          <span style={{color:c}}>{l}</span>
        </div>
      )}
    </div>
  </div>;
}

// ── Documents Table ────────────────────────────────────────────────────────
const PER=20;
function DocumentsTable({documents,onSelect}){
  const [search,setSearch]=useState(""),[status,setStatus]=useState("all");
  const [grade,setGrade]=useState("all"),[subj,setSubj]=useState("all"),[page,setPage]=useState(0);
  const SS={background:"rgba(255,255,255,.04)",border:"1px solid rgba(255,255,255,.1)",borderRadius:6,color:"#94a3b8",fontSize:12,padding:"5px 8px",cursor:"pointer"};
  const filtered=useMemo(()=>documents.filter(d=>{
    if(status!=="all"&&d.processing_status!==status)return false;
    if(grade!=="all"&&d.grade!==+grade)return false;
    if(subj!=="all"&&d.subject!==subj)return false;
    if(search){const q=search.toLowerCase();return d.title.toLowerCase().includes(q)||(d.subject||"").includes(q)||(d.document_type||"").includes(q);}
    return true;
  }),[documents,status,grade,subj,search]);
  const pages=Math.ceil(filtered.length/PER),slice=filtered.slice(page*PER,(page+1)*PER);
  return <div>
    <div style={{display:"flex",gap:8,marginBottom:14,flexWrap:"wrap"}}>
      <input value={search} onChange={e=>{setSearch(e.target.value);setPage(0);}} placeholder="Search…" style={{...SS,flex:1,minWidth:160,padding:"6px 12px"}}/>
      <select value={status} onChange={e=>{setStatus(e.target.value);setPage(0);}} style={SS}>
        <option value="all">All statuses</option>
        {Object.keys(STATUS_META).map(s=><option key={s} value={s}>{STATUS_META[s].label}</option>)}
      </select>
      <select value={grade} onChange={e=>{setGrade(e.target.value);setPage(0);}} style={SS}>
        <option value="all">All grades</option>
        {GRADES.map(g=><option key={g} value={g}>Grade {g}</option>)}
      </select>
      <select value={subj} onChange={e=>{setSubj(e.target.value);setPage(0);}} style={SS}>
        <option value="all">All subjects</option>
        {SUBJECTS.map(s=><option key={s} value={s}>{s.replace(/_/g," ")}</option>)}
      </select>
      <span style={{fontSize:12,color:"#475569",alignSelf:"center"}}>{filtered.length} docs</span>
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"separate",borderSpacing:"0 3px"}}>
        <thead><tr style={{fontSize:10,color:"#475569",letterSpacing:.08,textTransform:"uppercase"}}>
          {["Title","Type","Gr.","Subject","Status","Quality","Chunks",""].map(h=><th key={h} style={{padding:"5px 8px",textAlign:"left",fontWeight:600}}>{h}</th>)}
        </tr></thead>
        <tbody>{slice.map(d=><tr key={d.document_id} onClick={()=>onSelect(d)} style={{cursor:"pointer"}}
          onMouseEnter={e=>e.currentTarget.style.background="rgba(255,255,255,.04)"}
          onMouseLeave={e=>e.currentTarget.style.background="transparent"}>
          <td style={{padding:"7px 8px",color:"#e2e8f0",fontSize:12,maxWidth:240,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{d.title}</td>
          <td style={{padding:"7px 8px",color:"#64748b",fontSize:11}}>{d.document_type?.replace(/_/g," ")}</td>
          <td style={{padding:"7px 8px",color:"#94a3b8",fontSize:12,fontWeight:700}}>{d.grade}</td>
          <td style={{padding:"7px 8px",color:"#64748b",fontSize:11}}>{d.subject?.replace(/_/g," ")}</td>
          <td style={{padding:"7px 8px"}}><StatusBadge status={d.processing_status}/></td>
          <td style={{padding:"7px 8px",minWidth:90}}><QualityBar score={d.quality_score}/></td>
          <td style={{padding:"7px 8px",color:"#475569",fontSize:11}}>{d.chunk_count}</td>
          <td style={{padding:"7px 8px",color:"#475569",fontSize:11}}>›</td>
        </tr>)}
        </tbody>
      </table>
    </div>
    {pages>1&&<div style={{display:"flex",justifyContent:"center",gap:4,marginTop:14}}>
      <Btn onClick={()=>setPage(p=>Math.max(0,p-1))} disabled={page===0}>‹</Btn>
      <span style={{padding:"5px 14px",fontSize:12,color:"#64748b"}}>{page+1}/{pages}</span>
      <Btn onClick={()=>setPage(p=>Math.min(pages-1,p+1))} disabled={page===pages-1}>›</Btn>
    </div>}
  </div>;
}

// ── Doc Detail Drawer ──────────────────────────────────────────────────────
function DocDetail({doc,onClose,onApprove,onReject}){
  const fmt=n=>n?(n/1e6).toFixed(1)+"MB":"—";
  const rows=[["Type",doc.document_type?.replace(/_/g," ")],["Grade",doc.grade],["Subject",doc.subject?.replace(/_/g," ")],
    ["Phase",doc.phase],["Language",doc.language],["Curriculum",doc.curriculum||"CAPS"],
    ["Publisher",doc.publisher],["Author",doc.author],["Year",doc.publication_year],
    ["Pages",doc.page_count],["Size",fmt(doc.file_size_bytes)],["Chunks",doc.chunk_count],
    ["License",doc.license_status?.replace(/_/g," ")],["Training",doc.training_readiness?"✓ Ready":"✕ Not ready"]];
  return <div style={{position:"fixed",top:0,right:0,bottom:0,width:400,background:"#0d1117",borderLeft:"1px solid rgba(255,255,255,.08)",zIndex:100,display:"flex",flexDirection:"column",boxShadow:"-8px 0 32px rgba(0,0,0,.5)"}}>
    <div style={{padding:"18px 22px",borderBottom:"1px solid rgba(255,255,255,.06)"}}>
      <div style={{display:"flex",alignItems:"flex-start",gap:10}}>
        <div style={{flex:1}}>
          <div style={{fontSize:13,fontWeight:700,color:"#e2e8f0",lineHeight:1.4,marginBottom:7}}>{doc.title}</div>
          <StatusBadge status={doc.processing_status} size="md"/>
        </div>
        <button onClick={onClose} style={{background:"transparent",border:"none",color:"#475569",fontSize:18,cursor:"pointer"}}>✕</button>
      </div>
      <div style={{marginTop:12}}><QualityBar score={doc.quality_score}/></div>
    </div>
    <div style={{flex:1,overflowY:"auto",padding:"18px 22px"}}>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"9px 18px",marginBottom:18}}>
        {rows.map(([k,v])=><div key={k}>
          <div style={{fontSize:9,color:"#475569",letterSpacing:.1,textTransform:"uppercase",marginBottom:2}}>{k}</div>
          <div style={{fontSize:12,color:"#cbd5e1",fontWeight:500}}>{v||"—"}</div>
        </div>)}
      </div>
      {doc.reviewer_notes&&<div style={{background:"rgba(251,191,36,.06)",border:"1px solid rgba(251,191,36,.2)",borderRadius:8,padding:"11px 14px"}}>
        <div style={{fontSize:9,color:"#fbbf24",letterSpacing:.08,textTransform:"uppercase",marginBottom:3}}>Issues Flagged</div>
        <div style={{fontSize:12,color:"#fde68a"}}>{doc.reviewer_notes}</div>
      </div>}
    </div>
    <div style={{padding:"14px 22px",borderTop:"1px solid rgba(255,255,255,.07)",display:"flex",gap:7}}>
      {!["approved","training_ready","rejected","archived"].includes(doc.processing_status)&&<>
        <Btn onClick={()=>onApprove(doc)} variant="green" style={{flex:1}}>✓ Approve</Btn>
        <Btn onClick={()=>onReject(doc)} variant="red" style={{flex:1}}>✕ Reject</Btn>
      </>}
      <Btn onClick={onClose}>Close</Btn>
    </div>
  </div>;
}

// ── Review Queue ───────────────────────────────────────────────────────────
function ReviewQueue({tasks,onApprove,onReject}){
  const [filter,setFilter]=useState("all");
  const priorityColor={high:"#f87171",critical:"#ef4444",normal:"#94a3b8",low:"#64748b"};
  const shown=filter==="all"?tasks:tasks.filter(t=>t.priority===filter);
  if(!tasks.length) return <div style={{textAlign:"center",padding:"48px 0",color:"#475569"}}>
    <div style={{fontSize:32,marginBottom:8}}>✓</div>
    <div style={{fontSize:14,fontWeight:600}}>Review queue is empty</div>
  </div>;
  return <div>
    <div style={{display:"flex",gap:6,marginBottom:14}}>
      {["all","high","normal","low"].map(p=><Btn key={p} onClick={()=>setFilter(p)} variant={filter===p?"blue":"ghost"}>{p==="all"?"All":`${p.charAt(0).toUpperCase()+p.slice(1)}`}</Btn>)}
      <span style={{fontSize:12,color:"#64748b",alignSelf:"center",marginLeft:"auto"}}>{shown.length} tasks</span>
    </div>
    <div style={{display:"flex",flexDirection:"column",gap:7}}>
      {shown.map(t=><div key={t.task_id} style={{background:"rgba(255,255,255,.03)",border:"1px solid rgba(255,255,255,.07)",borderRadius:9,padding:"13px 16px",display:"flex",alignItems:"center",gap:12}}>
        <div style={{width:8,height:8,borderRadius:"50%",background:priorityColor[t.priority]||"#94a3b8",flexShrink:0}}/>
        <div style={{flex:1,minWidth:0}}>
          <div style={{fontSize:12,color:"#e2e8f0",fontWeight:600,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{t.title}</div>
          <div style={{fontSize:11,color:"#475569",marginTop:2}}>Gr.{t.grade} · {t.subject?.replace(/_/g," ")} · <span style={{color:"#64748b"}}>{t.reason}</span></div>
        </div>
        <QualityBar score={t.quality_score}/>
        {t.assigned_to&&<span style={{fontSize:10,color:"#64748b",whiteSpace:"nowrap"}}>{t.assigned_to.split(" ")[0]}</span>}
        <Btn onClick={()=>onApprove({document_id:t.document_id,processing_status:"needs_review"})} variant="green">✓</Btn>
        <Btn onClick={()=>onReject({document_id:t.document_id,processing_status:"needs_review"})} variant="red">✕</Btn>
      </div>)}
    </div>
  </div>;
}

// ── Jobs Monitor ───────────────────────────────────────────────────────────
function JobsMonitor({jobs}){
  const sc={success:"#22c55e",failed:"#f87171",running:"#fbbf24"};
  return <div style={{display:"flex",flexDirection:"column",gap:5}}>
    {jobs.map(j=>{const ago=Math.round((Date.now()-new Date(j.started_at).getTime())/60000);
      return <div key={j.job_id} style={{display:"flex",alignItems:"center",gap:10,padding:"7px 10px",borderRadius:7,background:"rgba(255,255,255,.02)"}}>
        <div style={{width:8,height:8,borderRadius:"50%",background:sc[j.status]||"#475569",flexShrink:0,
          boxShadow:j.status==="running"?`0 0 6px ${sc[j.status]}`:undefined}}/>
        <span style={{fontSize:11,color:"#94a3b8",minWidth:70,fontFamily:"monospace"}}>{j.stage}</span>
        <span style={{flex:1,fontSize:11,color:"#475569",fontFamily:"monospace",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{j.document_id}</span>
        <span style={{fontSize:10,color:sc[j.status]||"#475569",fontWeight:600}}>{j.status}</span>
        <span style={{fontSize:10,color:"#334155"}}>{ago}m ago</span>
      </div>;
    })}
  </div>;
}

// ── Search Panel ───────────────────────────────────────────────────────────
function SearchPanel({searchResults}){
  const [query,setQuery]=useState(""),[grade,setGrade]=useState("all"),[subj,setSubj]=useState("all");
  const [results,setResults]=useState([]),[searched,setSearched]=useState(false);
  const SS={background:"rgba(255,255,255,.04)",border:"1px solid rgba(255,255,255,.1)",borderRadius:6,color:"#94a3b8",fontSize:12,padding:"5px 8px"};
  const doSearch=()=>{
    let r=searchResults;
    if(grade!=="all") r=r.filter(x=>x.grade===+grade);
    if(subj!=="all") r=r.filter(x=>x.subject===subj);
    if(query) r=r.filter(x=>x.heading.toLowerCase().includes(query.toLowerCase())||x.content_preview.toLowerCase().includes(query.toLowerCase()));
    setResults(r); setSearched(true);
  };
  return <div>
    <div style={{display:"flex",gap:8,marginBottom:16,flexWrap:"wrap"}}>
      <input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>e.key==="Enter"&&doSearch()} placeholder="Search document chunks…" style={{...SS,flex:1,minWidth:220,padding:"8px 14px"}}/>
      <select value={grade} onChange={e=>setGrade(e.target.value)} style={SS}>
        <option value="all">All grades</option>
        {GRADES.map(g=><option key={g} value={g}>Grade {g}</option>)}
      </select>
      <select value={subj} onChange={e=>setSubj(e.target.value)} style={SS}>
        <option value="all">All subjects</option>
        {SUBJECTS.map(s=><option key={s} value={s}>{s.replace(/_/g," ")}</option>)}
      </select>
      <Btn onClick={doSearch} variant="blue">Search</Btn>
    </div>
    {!searched&&<div style={{fontSize:12,color:"#334155",padding:"10px 0"}}>Search across indexed document chunks. Results include page citations for AI attribution.</div>}
    {searched&&results.length===0&&<div style={{textAlign:"center",padding:"32px 0",color:"#475569",fontSize:13}}>No results found.</div>}
    <div style={{display:"flex",flexDirection:"column",gap:10}}>
      {results.map(r=><div key={r.chunk_id} style={{background:"rgba(255,255,255,.03)",border:"1px solid rgba(255,255,255,.07)",borderRadius:10,padding:"14px 18px"}}>
        <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",gap:10,marginBottom:7}}>
          <div>
            <div style={{fontSize:13,fontWeight:700,color:"#818cf8",marginBottom:3}}>{r.heading}</div>
            <div style={{fontSize:11,color:"#475569"}}>{r.title} · Gr.{r.grade} · {r.subject?.replace(/_/g," ")}</div>
          </div>
          <div style={{background:"rgba(129,140,248,.12)",border:"1px solid rgba(129,140,248,.2)",borderRadius:6,padding:"3px 9px",fontSize:11,color:"#818cf8",fontWeight:700,flexShrink:0}}>
            {Math.round(r.score*100)}%
          </div>
        </div>
        <div style={{fontSize:12,color:"#94a3b8",lineHeight:1.6,marginBottom:10}}>{r.content_preview}</div>
        <div style={{display:"flex",alignItems:"center",gap:8,fontSize:10,color:"#475569",borderTop:"1px solid rgba(255,255,255,.05)",paddingTop:8}}>
          <span>📄</span>
          <span style={{color:"#64748b"}}>{r.citation.section_path}</span>
          <span>·</span>
          <span>pp.{r.citation.page_start}–{r.citation.page_end}</span>
          <span style={{marginLeft:"auto",fontFamily:"monospace",color:"#334155"}}>{r.document_id}</span>
        </div>
      </div>)}
    </div>
  </div>;
}

// ── Training Panel ─────────────────────────────────────────────────────────
function TrainingPanel({datasets}){
  const [sel,setSel]=useState(null),[exportFormat,setExportFormat]=useState("jsonl");
  const [exportMsg,setExportMsg]=useState(null);
  const typeColor={qa:"#818cf8",summary:"#10b981",concept:"#06b6d4",rubric:"#f59e0b"};
  const doExport=ds=>{
    setExportMsg({ds_id:ds.dataset_id,fmt:exportFormat});
    setTimeout(()=>setExportMsg(null),3000);
  };
  return <div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12,marginBottom:20}}>
      {datasets.map(ds=>{
        const color=typeColor[ds.dataset_type]||"#818cf8";
        const sparkData=Array.from({length:12},(_,i)=>Math.floor(30+Math.random()*80));
        return <div key={ds.dataset_id} onClick={()=>setSel(sel?.dataset_id===ds.dataset_id?null:ds)}
          style={{background:"rgba(255,255,255,.03)",border:`1px solid ${sel?.dataset_id===ds.dataset_id?color+"50":"rgba(255,255,255,.07)"}`,borderRadius:12,padding:"16px 20px",cursor:"pointer",transition:"border-color .2s"}}>
          <div style={{display:"flex",alignItems:"flex-start",justifyContent:"space-between",marginBottom:10}}>
            <div>
              <div style={{fontSize:13,fontWeight:700,color:"#e2e8f0"}}>{ds.name}</div>
              <div style={{fontSize:11,color:"#475569",marginTop:2}}>v{ds.version} · {ds.split} · {ds.example_count.toLocaleString()} examples</div>
            </div>
            <span style={{fontSize:10,background:`${color}18`,color,border:`1px solid ${color}30`,borderRadius:20,padding:"2px 10px",fontWeight:700,textTransform:"uppercase",letterSpacing:.06}}>{ds.dataset_type}</span>
          </div>
          <div style={{display:"flex",gap:16,marginBottom:10}}>
            <div><div style={{fontSize:9,color:"#475569",textTransform:"uppercase",letterSpacing:.08,marginBottom:2}}>Human Reviewed</div>
              <div style={{fontSize:16,fontWeight:700,color}}>{ds.human_reviewed_pct}%</div></div>
            <div><div style={{fontSize:9,color:"#475569",textTransform:"uppercase",letterSpacing:.08,marginBottom:2}}>Avg Quality</div>
              <div style={{fontSize:16,fontWeight:700,color:"#10b981"}}>{Math.round(ds.avg_quality*100)}%</div></div>
            <div style={{marginLeft:"auto",display:"flex",alignItems:"flex-end"}}>
              <Sparkline data={sparkData} color={color} height={32} width={90}/>
            </div>
          </div>
          <div style={{height:4,borderRadius:3,background:"rgba(255,255,255,.06)"}}>
            <div style={{height:"100%",borderRadius:3,background:color,width:`${ds.human_reviewed_pct}%`}}/>
          </div>
        </div>;
      })}
    </div>
    {sel&&<Card title={`Dataset: ${sel.name}`}>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginBottom:16}}>
        <div>
          <div style={{fontSize:11,color:"#64748b",marginBottom:8}}>Grade Distribution</div>
          {Object.entries(sel.grade_dist).map(([g,v])=><BarH key={g} label={`Grade ${g}`} value={v} max={Math.max(...Object.values(sel.grade_dist))} color={typeColor[sel.dataset_type]}/>)}
        </div>
        <div>
          <div style={{fontSize:11,color:"#64748b",marginBottom:8}}>Subject Distribution</div>
          {Object.entries(sel.subject_dist).map(([s,v])=><BarH key={s} label={s.replace(/_/g," ")} value={v} max={Math.max(...Object.values(sel.subject_dist))} color="#06b6d4"/>)}
        </div>
      </div>
      <div style={{display:"flex",gap:8,alignItems:"center",marginTop:12}}>
        <span style={{fontSize:12,color:"#475569"}}>Export as:</span>
        {["jsonl","csv","parquet"].map(f=><Btn key={f} onClick={()=>setExportFormat(f)} variant={exportFormat===f?"blue":"ghost"} style={{fontSize:11}}>{f.toUpperCase()}</Btn>)}
        <Btn onClick={()=>doExport(sel)} variant="green">⬇ Export {sel.example_count.toLocaleString()} examples</Btn>
        {sel.export_path&&<span style={{fontSize:10,color:"#22c55e",marginLeft:4}}>✓ Previously exported</span>}
      </div>
      {exportMsg&&<div style={{marginTop:10,padding:"8px 14px",borderRadius:7,background:"rgba(34,197,94,.08)",border:"1px solid rgba(34,197,94,.2)",fontSize:12,color:"#22c55e"}}>
        ✓ Export queued: {exportMsg.ds_id}.{exportMsg.fmt} — check ./exports/ directory</div>}
      <div style={{marginTop:14,padding:"10px 14px",borderRadius:8,background:"rgba(129,140,248,.06)",border:"1px solid rgba(129,140,248,.15)"}}>
        <div style={{fontSize:10,color:"#818cf8",letterSpacing:.08,textTransform:"uppercase",marginBottom:6}}>Train/Val/Test Split</div>
        <div style={{display:"flex",gap:3,height:12,borderRadius:3,overflow:"hidden"}}>
          <div style={{flex:7,background:"rgba(129,140,248,.6)"}}/>
          <div style={{flex:1.5,background:"rgba(6,182,212,.6)"}}/>
          <div style={{flex:1.5,background:"rgba(248,113,113,.5)"}}/>
        </div>
        <div style={{display:"flex",gap:16,marginTop:6,fontSize:10,color:"#64748b"}}>
          <span style={{color:"#818cf8"}}>70% train</span>
          <span style={{color:"#06b6d4"}}>15% val</span>
          <span style={{color:"#f87171"}}>15% test</span>
        </div>
      </div>
    </Card>}
  </div>;
}

// ── Monitoring Panel ───────────────────────────────────────────────────────
function FeedbackStream({feedbackItems}){
  const [stream,setStream]=useState(feedbackItems.slice(0,5));
  const [idx,setIdx]=useState(5);
  useEffect(()=>{
    const t=setInterval(()=>{
      setIdx(i=>{
        const next=feedbackItems[i%feedbackItems.length];
        setStream(s=>[next,...s].slice(0,8));
        return i+1;
      });
    },2800);
    return ()=>clearInterval(t);
  },[feedbackItems]);
  const typeColor={incorrect_answer:"#f87171",missing_document:"#fbbf24",outdated_document:"#f59e0b",bad_citation:"#818cf8",wrong_grade_subject:"#06b6d4"};
  return <div style={{display:"flex",flexDirection:"column",gap:5}}>
    {stream.map((fb,i)=>{
      const color=typeColor[fb.feedback_type]||"#94a3b8";
      const ago=Math.round((Date.now()-new Date(fb.created_at).getTime())/60000);
      return <div key={`${fb.feedback_id}-${i}`} style={{
        display:"flex",alignItems:"center",gap:10,padding:"8px 12px",borderRadius:7,
        background:`${color}08`,border:`1px solid ${color}20`,
        animation:i===0?"fadeIn .3s ease":"none",
      }}>
        <div style={{width:7,height:7,borderRadius:"50%",background:color,flexShrink:0}}/>
        <span style={{fontSize:11,color,fontWeight:600,minWidth:120,whiteSpace:"nowrap"}}>{fb.feedback_type.replace(/_/g," ")}</span>
        <span style={{fontSize:11,color:"#475569",flex:1,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{fb.details}</span>
        <span style={{fontSize:10,color:"#334155",whiteSpace:"nowrap"}}>{ago}m ago</span>
        {fb.resolved?<span style={{fontSize:10,color:"#22c55e"}}>✓</span>:<span style={{fontSize:10,color:"#fbbf24"}}>•</span>}
      </div>;
    })}
  </div>;
}

function MonitoringPanel({monitoring,feedbackItems}){
  const series=monitoring.metric_series||[];
  const kpis=[
    {label:"7-day Ingestion",value:monitoring.ingestion_rate_7d,unit:"docs",color:"#818cf8"},
    {label:"Approval Rate",value:`${Math.round(monitoring.approval_rate*100)}%`,color:"#22c55e"},
    {label:"Avg Quality",value:`${Math.round(monitoring.avg_quality_score*100)}%`,color:"#10b981"},
    {label:"Job Failures 24h",value:monitoring.failed_jobs_24h,color:"#f87171"},
    {label:"Extraction Fail Rate",value:`${Math.round(monitoring.extraction_failure_rate*100)}%`,color:"#fbbf24"},
    {label:"Pending Reviews",value:monitoring.pending_reviews||0,color:"#06b6d4"},
  ];
  return <div>
    <div style={{display:"flex",gap:10,flexWrap:"wrap",marginBottom:16}}>
      {kpis.map(k=><div key={k.label} style={{background:"rgba(255,255,255,.03)",border:"1px solid rgba(255,255,255,.07)",borderRadius:10,padding:"14px 18px",flex:1,minWidth:130}}>
        <div style={{fontSize:24,fontWeight:800,color:k.color,lineHeight:1}}>{k.value}{k.unit?" "+k.unit:""}</div>
        <div style={{fontSize:11,color:"#475569",marginTop:4}}>{k.label}</div>
      </div>)}
    </div>
    {monitoring.alerts?.length>0&&<div style={{marginBottom:16}}>
      {monitoring.alerts.map((a,i)=><div key={i} style={{display:"flex",gap:10,alignItems:"center",padding:"9px 14px",borderRadius:8,background:"rgba(251,191,36,.06)",border:"1px solid rgba(251,191,36,.2)",marginBottom:6}}>
        <span style={{fontSize:14}}>⚠</span>
        <span style={{fontSize:12,color:"#fde68a"}}>{a}</span>
      </div>)}
    </div>}
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:14,marginBottom:16}}>
      <Card title="Ingestion vs Failures (24h)">
        <div style={{display:"flex",gap:16,alignItems:"flex-end",marginBottom:8}}>
          <MetricChart series={series} metric="ingestion" color="#818cf8" height={56}/>
          <div style={{fontSize:11,color:"#475569"}}>
            <div style={{display:"flex",alignItems:"center",gap:5,marginBottom:4}}><div style={{width:10,height:2,background:"#818cf8"}}/> Ingested</div>
            <div style={{display:"flex",alignItems:"center",gap:5}}><div style={{width:10,height:2,background:"#f87171"}}/> Failures</div>
          </div>
        </div>
        <MetricChart series={series} metric="failures" color="#f87171" height={32}/>
      </Card>
      <Card title="Feedback Summary (30 days)">
        <div style={{display:"flex",gap:16,alignItems:"center"}}>
          <DonutChart data={FEEDBACK_TYPES.map((t,i)=>({value:monitoring.feedback_summary[t]||0,color:["#f87171","#fbbf24","#f59e0b","#818cf8","#06b6d4"][i]}))} size={100}/>
          <div style={{flex:1}}>
            {FEEDBACK_TYPES.map((t,i)=>{
              const colors=["#f87171","#fbbf24","#f59e0b","#818cf8","#06b6d4"];
              return <div key={t} style={{display:"flex",justifyContent:"space-between",fontSize:11,marginBottom:4}}>
                <span style={{color:colors[i]}}>{t.replace(/_/g," ")}</span>
                <span style={{color:"#94a3b8",fontWeight:700}}>{monitoring.feedback_summary[t]||0}</span>
              </div>;
            })}
          </div>
        </div>
      </Card>
    </div>
    <Card title="Live Feedback Stream" subtitle="Real-time user feedback ingestion — auto-creates review tasks for actionable items">
      <FeedbackStream feedbackItems={feedbackItems}/>
    </Card>
    {monitoring.stale_documents?.length>0&&<Card title="Stale Documents" subtitle="Stuck in early processing stages for >90 days">
      <div style={{display:"flex",flexDirection:"column",gap:5}}>
        {monitoring.stale_documents.map(d=><div key={d.document_id} style={{display:"flex",alignItems:"center",gap:12,padding:"7px 10px",borderRadius:7,background:"rgba(248,113,113,.04)",border:"1px solid rgba(248,113,113,.1)"}}>
          <div style={{flex:1,fontSize:12,color:"#e2e8f0",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{d.title}</div>
          <StatusBadge status={d.processing_status}/>
          <span style={{fontSize:11,color:"#f87171",fontWeight:700,minWidth:60,textAlign:"right"}}>{d.days_stale}d stale</span>
        </div>)}
      </div>
    </Card>}
  </div>;
}

// ── Main App ───────────────────────────────────────────────────────────────
export default function App(){
  const [tab,setTab]=useState("overview");
  const [docs,setDocs]=useState(DATA.documents);
  const [tasks,setTasks]=useState(DATA.reviewTasks);
  const [stats,setStats]=useState(DATA.stats);
  const [selected,setSelected]=useState(null);
  const [toast,setToast]=useState(null);

  const showToast=(msg,color="#22c55e")=>{
    setToast({msg,color});
    setTimeout(()=>setToast(null),2800);
  };
  const handleApprove=doc=>{
    setDocs(ds=>ds.map(d=>d.document_id===doc.document_id?{...d,processing_status:"approved"}:d));
    setTasks(ts=>ts.filter(t=>t.document_id!==doc.document_id));
    setStats(s=>({...s,approved:(s.approved||0)+1,needs_review:Math.max(0,(s.needs_review||0)-1)}));
    if(selected?.document_id===doc.document_id) setSelected({...selected,processing_status:"approved"});
    showToast(`✓ Approved: ${doc.title?.substring(0,40)}…`,"#22c55e");
  };
  const handleReject=doc=>{
    setDocs(ds=>ds.map(d=>d.document_id===doc.document_id?{...d,processing_status:"rejected"}:d));
    setTasks(ts=>ts.filter(t=>t.document_id!==doc.document_id));
    setStats(s=>({...s,rejected:(s.rejected||0)+1,needs_review:Math.max(0,(s.needs_review||0)-1)}));
    if(selected?.document_id===doc.document_id) setSelected({...selected,processing_status:"rejected"});
    showToast(`✕ Rejected: ${doc.title?.substring(0,40)}…`,"#f87171");
  };

  return (
    <div style={{minHeight:"100vh",background:"#080b14",color:"#e2e8f0",fontFamily:"system-ui,-apple-system,sans-serif"}}>
      <style>{`
        *{box-sizing:border-box;-webkit-font-smoothing:antialiased}
        ::-webkit-scrollbar{width:5px;height:5px}
        ::-webkit-scrollbar-track{background:transparent}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:4px}
        input,select{outline:none}
        @keyframes fadeIn{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}
      `}</style>

      {/* Header */}
      <div style={{borderBottom:"1px solid rgba(255,255,255,.06)",padding:"12px 28px",display:"flex",alignItems:"center",gap:14,background:"rgba(255,255,255,.01)",position:"sticky",top:0,zIndex:50,backdropFilter:"blur(10px)"}}>
        <div>
          <div style={{fontSize:17,fontWeight:800,letterSpacing:-.02,color:"#e2e8f0"}}>
            Eduboost <span style={{color:"#818cf8"}}>ETL</span> Admin
          </div>
          <div style={{fontSize:9,color:"#475569",letterSpacing:.1,marginTop:1}}>DOCUMENT & TRAINING DATA PIPELINE — PHASES 0–12</div>
        </div>
        <div style={{flex:1}}/>
        <div style={{display:"flex",alignItems:"center",gap:5}}>
          <div style={{width:7,height:7,borderRadius:"50%",background:"#22c55e",boxShadow:"0 0 6px #22c55e"}}/>
          <span style={{fontSize:11,color:"#22c55e",fontWeight:600}}>Active</span>
        </div>
        <div style={{background:"rgba(251,191,36,.08)",border:"1px solid rgba(251,191,36,.2)",borderRadius:7,padding:"4px 11px",fontSize:11,color:"#fbbf24",fontWeight:600}}>
          ⚠ {stats.pending_reviews} pending
        </div>
        <div style={{background:"rgba(16,185,129,.08)",border:"1px solid rgba(16,185,129,.2)",borderRadius:7,padding:"4px 11px",fontSize:11,color:"#10b981",fontWeight:600}}>
          ✓ {stats.training_ready_count} training ready
        </div>
      </div>

      {/* Tabs */}
      <div style={{padding:"10px 28px 0",display:"flex",gap:2,borderBottom:"1px solid rgba(255,255,255,.05)",overflowX:"auto"}}>
        {TABS.map(([key,label])=><button key={key} onClick={()=>setTab(key)} style={{
          padding:"8px 16px",borderRadius:"7px 7px 0 0",fontSize:12,fontWeight:tab===key?700:500,
          cursor:"pointer",border:"none",whiteSpace:"nowrap",
          background:tab===key?"rgba(129,140,248,.12)":"transparent",
          color:tab===key?"#818cf8":"#475569",
          borderBottom:tab===key?"2px solid #818cf8":"2px solid transparent",
        }}>{label}</button>)}
      </div>

      {/* Body */}
      <div style={{padding:"24px 28px",maxWidth:1520}}>

        {tab==="overview"&&<div>
          <div style={{display:"flex",gap:10,flexWrap:"wrap",marginBottom:20}}>
            <StatCard icon="📄" label="Total Documents" value={stats.total} color="#e2e8f0"/>
            <StatCard icon="✓" label="Approved" value={stats.approved||0} color="#22c55e"/>
            <StatCard icon="🤖" label="Training Ready" value={stats.training_ready_count||0} color="#10b981"/>
            <StatCard icon="🔍" label="Indexed" value={stats.indexed_count||0} color="#06b6d4"/>
            <StatCard icon="⚠" label="Needs Review" value={stats.needs_review||0} color="#fbbf24"/>
            <StatCard icon="✕" label="Rejected" value={stats.rejected||0} color="#f87171"/>
            <StatCard icon="⌇" label="Avg Quality" value={`${Math.round((stats.avg_quality_score||0)*100)}%`} color="#818cf8" sub="across all docs"/>
          </div>
          <Card title="Pipeline Stage Distribution"><PipelineFlow stats={stats}/></Card>
          <div style={{display:"grid",gridTemplateColumns:"2fr 1fr",gap:14}}>
            <Card title="Document Status Breakdown">
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>
                {Object.entries(STATUS_META).map(([s,m])=>{
                  const n=stats[s]||0,sparkData=Array.from({length:8},()=>Math.floor(Math.random()*n+1));
                  return <div key={s} style={{display:"flex",alignItems:"center",gap:10,padding:"9px 12px",borderRadius:8,background:m.bg,border:`1px solid ${m.color}28`}}>
                    <div><div style={{fontSize:18,fontWeight:800,color:m.color}}>{n}</div>
                      <div style={{fontSize:9,color:m.color,fontWeight:600,letterSpacing:.06,textTransform:"uppercase"}}>{m.label}</div>
                    </div>
                    <div style={{marginLeft:"auto"}}><Sparkline data={sparkData} color={m.color} height={24} width={60}/></div>
                  </div>;
                })}
              </div>
            </Card>
            <div>
              <Card title="Recent Jobs"><JobsMonitor jobs={DATA.jobs.slice(0,6)}/></Card>
              <Card title="Recent Docs">
                {docs.slice(0,5).map(d=><div key={d.document_id} onClick={()=>setSelected(d)}
                  style={{display:"flex",alignItems:"center",gap:8,padding:"6px 0",borderBottom:"1px solid rgba(255,255,255,.04)",cursor:"pointer"}}>
                  <div style={{flex:1,minWidth:0}}>
                    <div style={{fontSize:12,color:"#cbd5e1",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{d.title}</div>
                    <div style={{fontSize:10,color:"#475569"}}>Gr.{d.grade} · {(d.subject||"").replace(/_/g," ")}</div>
                  </div>
                  <StatusBadge status={d.processing_status}/>
                </div>)}
              </Card>
            </div>
          </div>
        </div>}

        {tab==="documents"&&<Card title={`Document Registry — ${docs.length} documents`}>
          <DocumentsTable documents={docs} onSelect={setSelected}/>
        </Card>}

        {tab==="gaps"&&<Card title="Content Coverage Matrix" subtitle="Approved document coverage by grade × subject for each document type. Red = missing, yellow = exists but unreviewed.">
          <GapMatrix documents={docs}/>
        </Card>}

        {tab==="review"&&<Card title="Human Review Queue" subtitle="Documents that failed validation or received user feedback.">
          <ReviewQueue tasks={tasks} onApprove={handleApprove} onReject={handleReject}/>
        </Card>}

        {tab==="search"&&<Card title="Phase 9 — Full-Text Search" subtitle="Search approved document chunks. Results include source citations for AI response attribution.">
          <SearchPanel searchResults={DATA.searchResults}/>
        </Card>}

        {tab==="training"&&<div>
          <div style={{fontSize:16,fontWeight:700,color:"#e2e8f0",marginBottom:16}}>Phase 10 — Training Dataset Builder</div>
          <TrainingPanel datasets={DATA.datasets}/>
        </div>}

        {tab==="monitoring"&&<div>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:18}}>
            <div>
              <div style={{fontSize:16,fontWeight:700,color:"#e2e8f0"}}>Phase 12 — Monitoring & Feedback Loop</div>
              <div style={{fontSize:12,color:"#475569",marginTop:2}}>Last snapshot: {new Date(DATA.monitoring.generated_at).toLocaleString()}</div>
            </div>
          </div>
          <MonitoringPanel monitoring={DATA.monitoring} feedbackItems={DATA.feedbackItems}/>
        </div>}

        {tab==="jobs"&&<Card title="Processing Jobs" subtitle="Recent ETL job executions across all pipeline stages.">
          <div style={{display:"flex",gap:14,marginBottom:14}}>
            {["success","running","failed"].map(s=>{const n=DATA.jobs.filter(j=>j.status===s).length;
              const col=s==="success"?"#22c55e":s==="failed"?"#f87171":"#fbbf24";
              return <div key={s} style={{display:"flex",alignItems:"center",gap:6,fontSize:12}}>
                <div style={{width:8,height:8,borderRadius:"50%",background:col}}/>
                <span style={{color:col,fontWeight:600}}>{n}</span>
                <span style={{color:"#475569"}}>{s}</span>
              </div>;})}
          </div>
          <JobsMonitor jobs={DATA.jobs}/>
        </Card>}
      </div>

      {selected&&<DocDetail doc={selected} onClose={()=>setSelected(null)} onApprove={handleApprove} onReject={handleReject}/>}
      {toast&&<div style={{position:"fixed",bottom:24,left:"50%",transform:"translateX(-50%)",background:"#0d1117",border:`1px solid ${toast.color}35`,borderRadius:9,padding:"11px 22px",color:toast.color,fontWeight:600,fontSize:13,boxShadow:"0 8px 28px rgba(0,0,0,.5)",zIndex:200,animation:"fadeIn .2s ease"}}>{toast.msg}</div>}
    </div>
  );
}
