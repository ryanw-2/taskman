import React from 'react'
import { Link } from 'react-router-dom'

export function Home() {
  return (
    //Creates full screen container
    <div className="h-screen w-full flex 
    items-center justify-center bg-neutral-900">
{/* 
      <Link to="/">Home</Link>
      <Link to="/calendar">Calendar</Link>
      <Link to="/smartsearch">SmartSearch</Link>
      <Link to="/checklist">Checklist</Link> */}
      {/*Creates Grid container*/}
      <div className="grid h-21/24 w-full
      grid-flow-col grid-rows-9 gap-4 p-10
      xl:m-2 lg:m-2 md:m-2">

        {/* (Top) Name/Greeting */}
        <div className='col-start-1 col-end-3 row-start-1 row-end-2 rounded-lg bg-drab-500'></div>

        {/* (Top) Stat 1 */}
        <div className='col-start-8 col-end-9 row-start-1 row-end-2 rounded-lg bg-battleship-500'></div>

        {/* (Top) Stat 2 */}
        <div className='col-start-9 col-end-10 row-start-1 row-end-2 rounded-lg bg-jet-500'></div>

        {/* Calendar */}
        <div className='col-start-1 col-end-5 row-start-2 row-end-9 rounded-lg bg-sea-500'></div>

        {/* Smart Search */}
        <div className='col-start-5 col-end-7 row-start-2 row-end-9 rounded-lg bg-timber-500'></div>

        {/* Check List */}
        <div className='col-start-7 col-end-9 row-start-2 row-end-9 rounded-lg bg-timber-500'></div>

        {/* Secondary Widgets */}
        <div className='col-start-9 cold-end-10 row-start-2 row-end-9 rounded-lg bg-sea-500'></div>

        {/* (Bottom) Information */}
        <div className='col-start-1 col-end-4 row-start-9 row-end-10 rounded-lg bg-jet-500'></div>        
      </div>
    </div>
  )
}

export default Home