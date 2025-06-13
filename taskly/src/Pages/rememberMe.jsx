        {/* Calendar */}
        <div id="calendar" className="grid-item calendar">
          <h3>
            <span>
              {month} {day}, {year}
            </span>
          </h3>
        </div>

        {/* Smart Search */}
        <div id="smartsearch" className="grid-item smart-search">
          <h3>Taskly Ask</h3>
        </div>

        {/* Check List */}
        <div id="checklist" className="grid-item checklist">
          <h3>Checklist</h3>
        </div>

        {/* Secondary Widgets 1*/}
        <div
          id="secondary_1"
          ref={buttonRefList.current[0]}
          onClick={() => handleButtonClick(0)}
          className="grid-item secondary-widget1"
        >
          <img src={timer} alt="timer icon" />
        </div>

        {/* Secondary Widgets 2 */}
        <div
          id="secondary_2"
          ref={buttonRefList.current[1]}
          onClick={() => handleButtonClick(1)}
          className="grid-item secondary-widget2"
        >
          <img src={note} alt="notepad icon" />
        </div>