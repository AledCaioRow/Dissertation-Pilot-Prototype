# DB_CONTEXT — student_club (frozen)

This is the frozen `{{DB_CONTEXT}}` block. Generated once from the database and used
verbatim in every model call. Do not regenerate it per call.

## Schema (from student_club.md)
member(member_id, first_name, last_name, email, position, t_shirt_size, phone, zip, link_to_major)
major(major_id, major_name, department, college)
event(event_id, event_name, event_date, type, notes, location, status)
attendance(link_to_event, link_to_member)
budget(budget_id, category, spent, remaining, amount, event_status, link_to_event)
expense(expense_id, expense_description, expense_date, cost, approved, link_to_member, link_to_budget)
income(income_id, date_received, amount, source, notes, link_to_member)
zip_code(zip_code, type, city, county, state, short_state)

Foreign keys:
member.zip -> zip_code.zip_code
member.link_to_major -> major.major_id
attendance.link_to_event -> event.event_id
attendance.link_to_member -> member.member_id
budget.link_to_event -> event.event_id
expense.link_to_member -> member.member_id
expense.link_to_budget -> budget.budget_id
income.link_to_member -> member.member_id

## Evidence
- A member's full name is first_name + ' ' + last_name.
- attendance has one row per member per event attended; count rows for turnout.
- event_date is text such as 2020-03-10T12:00:00; expense_date is text such as YYYY-MM-DD.
- event.type is the kind of event, such as game, social, election.
- event.status is one of Open, Closed, Planning.
- budget.event_status is one of Closed, Open, Planning. Closed: spent and remaining no longer change. Open: they change with new expenses. Planning: not started, they do not change yet.
- budget.category is the area budgeted for, such as advertisement, food, parking.
- budget.spent (dollars) is summarised from the expense table.
- budget.remaining (dollars) = amount - spent; remaining < 0 means the cost exceeded the budget.
- budget.amount (dollars) = spent + remaining.
- expense.cost is in dollars; expense.approved is true or false.
- income.amount is in dollars; income.source is where funds come from, such as dues or the annual university allocation.
- member.zip is the ZIP code of the member's hometown.
- zip_code.type is one of Standard, PO Box, Unique.
- All money is in US dollars.

## Sample data
SAMPLE DATA — this is a SUBSET of the database, not the whole of it. Use it to see how values look; do not assume these are all the rows.

Example rows (first 10 per table by primary key):
member: member_id=rec1x5zBFIqoOuPW8, first_name=Angela, last_name=Sanders, email=angela.sanders@lpu.edu, position=Member, t_shirt_size=Medium, phone=(651) 928-4507, zip=55108, link_to_major=recxK3MHQFbR9J5uO
member: member_id=rec280Sk7o31iG0Tx, first_name=Grant, last_name=Gilmour, email=grant.gilmour@lpu.edu, position=Member, t_shirt_size=X-Large, phone=403-555-1310, zip=29440, link_to_major=rec7BxKpjJ7bNph3O
member: member_id=rec28ORZgcm1dtqBZ, first_name=Luisa, last_name=Guidi, email=luisa.guidi@lpu.edu, position=Member, t_shirt_size=Medium, phone=442-555-5882, zip=10002, link_to_major=recdIBgeU38UbV2sy
member: member_id=rec2a03QXbFQAUZ7X, first_name=Randy, last_name=Woodard, email=randy.woodard@lpu.edu, position=Inactive, t_shirt_size=X-Large, phone=490-555-8460, zip=8021, link_to_major=NULL
member: member_id=rec3pH4DxMcWHMRB7, first_name=Connor, last_name=Hilton, email=connor.hilton@lpu.edu, position=Member, t_shirt_size=X-Large, phone=454-555-7970, zip=48236, link_to_major=recaJdSK83k6ekRJL
member: member_id=rec4BLdZHS2Blfp4v, first_name=Sacha, last_name=Harrison, email=sacha.harrison@lpu.edu, position=President, t_shirt_size=Large, phone=840-555-4781, zip=7080, link_to_major=recCk8lCDOTRp6rKN
member: member_id=rec4O9rmGnLx3j8vt, first_name=Christof, last_name=Nielson, email=christof.nielson@lpu.edu, position=Member, t_shirt_size=X-Large, phone=(701) 932-1903, zip=58102, link_to_major=rectOU2QnznthfWv7
member: member_id=rec75vvFxgYtHmqxY, first_name=Carlo, last_name=Jacobs, email=carlo.jacobs@lpu.edu, position=Member, t_shirt_size=Medium, phone=928-555-2577, zip=11104, link_to_major=recf3mPmWq4JXKf4L
member: member_id=recD078PnS3x2doBe, first_name=Phillip, last_name=Cullen, email=phillip.cullen@lpu.edu, position=Vice President, t_shirt_size=X-Large, phone=905-555-5035, zip=1020, link_to_major=rec9CqGCGV8Y8rOSY
member: member_id=recEFd8s6pkrTt4Pz, first_name=Matthew, last_name=Snay, email=matt.snay@lpu.edu, position=Member, t_shirt_size=Large, phone=260-555-4328, zip=7002, link_to_major=recxRBSgVYeSEGvyo
major: major_id=rec06DF6vZ1CyPKpc, major_name=Outdoor Product Design and Development, department=School of Applied Sciences, Technolog..., college=College of Agriculture and Applied Sc...
major: major_id=rec09LedkREyskCNv, major_name=Agricultural Communication, department=School of Applied Sciences, Technolog..., college=College of Agriculture and Applied Sc...
major: major_id=rec0Eanv576RhQllI, major_name=Fisheries and Aquatic Sciences, department=Watershed Sciences Department, college=College of Natural Resources
major: major_id=rec0xRZtkzxrg8kj2, major_name=Finance, department=Economics and Finance Department, college=School of Business
major: major_id=rec1N0upiVLy5esTO, major_name=Forest Ecology and Management, department=Wildland Resources Department, college=College of Natural Resources
major: major_id=rec1SiX2nFrkbTleH, major_name=Biological Engineering, department=Biological Engineering Department, college=College of Engineering
major: major_id=rec2joRXA5HOSHE9a, major_name=Ornamental Horticulture Certificate, department=Plants, Soils, and Climate Department, college=College of Agriculture and Applied Sc...
major: major_id=rec3pZhvStMoNbVgy, major_name=Religious Studies, department=Religious Studies Program, college=College of Humanities and Social Scie...
major: major_id=rec42NIsgijDV6aDE, major_name=Statistics, department=Mathematics and Statistics Department, college=College of Science
major: major_id=rec6OKJlX4eg3hOLe, major_name=Journalism, department=Journalism and Communication Department, college=College of Humanities and Social Scie...
event: event_id=rec0Si5cQ4rJRVzd6, event_name=March Meeting, event_date=2020-03-10T12:00:00, type=Meeting, notes=NULL, location=MU 215, status=Open
event: event_id=rec0akZnLLpGUloLH, event_name=Officers meeting - January, event_date=2020-01-14T09:30:00, type=Meeting, notes=NULL, location=NULL, status=Open
event: event_id=rec0dZPcWXF0QjNnE, event_name=Spring Elections, event_date=2019-11-24T09:00:00, type=Election, notes=All active members can vote for new o..., location=MU 215, status=Open
event: event_id=rec180D2MI4EpckHy, event_name=Officers meeting - March, event_date=2020-03-10T09:30:00, type=Meeting, notes=NULL, location=NULL, status=Planning
event: event_id=rec2N69DMcrqN9PJC, event_name=Women's Soccer, event_date=2019-10-05T12:00:00, type=Game, notes=Attend Women's soccer game as a group., location=Campus Soccer/Lacrosse stadium, status=Closed
event: event_id=rec2mJrCofveboaz6, event_name=April Speaker, event_date=2020-04-21T12:00:00, type=Guest Speaker, notes=NULL, location=MU 215, status=Planning
event: event_id=rec5XDvJLyxDsGZWc, event_name=Laugh Out Loud, event_date=2019-10-24T13:00:00, type=Social, notes=Semester social event. Optional atten..., location=900 E. Washington St., status=Closed
event: event_id=recAlAwtBZ0Fqbr5K, event_name=March Speaker, event_date=2020-03-24T12:00:00, type=Guest Speaker, notes=NULL, location=MU 215, status=Open
event: event_id=recEVTik3MlqbvLFi, event_name=October Speaker, event_date=2019-10-22T12:00:00, type=Guest Speaker, notes=NULL, location=MU 215, status=Closed
event: event_id=recGxVCwaLW3mDIa3, event_name=Football game, event_date=2019-09-12T06:00:00, type=Game, notes=Attend school football game as a group., location=Campus Football stadium, status=Closed
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=rec28ORZgcm1dtqBZ
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recD078PnS3x2doBe
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recEFd8s6pkrTt4Pz
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recEymrwCUKxiiosI
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recJMazpPVexyFYTc
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recL94zpn6Xh6kQii
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recP6DJPyi5donvXL
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recQaxyXBQG5BBtD0
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recT92PyyZCGq1R68
attendance: link_to_event=rec2N69DMcrqN9PJC, link_to_member=recTjHY5xXhvkCdVT
budget: budget_id=rec0QmEc3cSQFQ6V2, category=Advertisement, spent=67.81, remaining=7.19, amount=75, event_status=Closed, link_to_event=recI43CzsZ0Q625ma
budget: budget_id=rec1bG6HSft7XIvTP, category=Food, spent=121.14, remaining=28.86, amount=150, event_status=Closed, link_to_event=recggMW2eyCYceNcy
budget: budget_id=rec1z6ISJU2HdIsVm, category=Food, spent=20.2, remaining=-0.199999999999999, amount=20, event_status=Closed, link_to_event=recJ4Witp9tpjaugn
budget: budget_id=rec33PFqxLtnp80RJ, category=Speaker Gifts, spent=0.0, remaining=25.0, amount=25, event_status=Open, link_to_event=recHaMmaKyfktt5fW
budget: budget_id=rec4DYUKBHMPZXWB2, category=Food, spent=0.0, remaining=150.0, amount=150, event_status=Open, link_to_event=recHaMmaKyfktt5fW
budget: budget_id=rec4yM47hEjVVsCuq, category=Parking, spent=0.0, remaining=10.0, amount=10, event_status=Open, link_to_event=recs4x1BYWAsU2SKg
budget: budget_id=rec59vErJo51glQRb, category=Advertisement, spent=0.0, remaining=55.0, amount=55, event_status=Open, link_to_event=recwM7GMBSLDlb1Ix
budget: budget_id=rec5V70sIuIgpOzDT, category=Food, spent=173.06, remaining=-23.06, amount=150, event_status=Closed, link_to_event=recI43CzsZ0Q625ma
budget: budget_id=recFZ47e0eVqcQD9O, category=Advertisement, spent=0.0, remaining=75.0, amount=75, event_status=Open, link_to_event=recHaMmaKyfktt5fW
budget: budget_id=recHzdM40gk9a6AdY, category=Speaker Gifts, spent=0.0, remaining=25.0, amount=25, event_status=Planning, link_to_event=rec2mJrCofveboaz6
expense: expense_id=rec017x6R3hQqkLAo, expense_description=Post Cards, Posters, expense_date=2019-08-20, cost=122.06, approved=true, link_to_member=rec4BLdZHS2Blfp4v, link_to_budget=recvKTAWAFKkVNnXQ
expense: expense_id=rec1nIjoZKTYayqZ6, expense_description=Water, Cookies, expense_date=2019-10-08, cost=20.2, approved=true, link_to_member=recro8T1MPMwRadVH, link_to_budget=recy8KY5bUdzF81vv
expense: expense_id=rec1oMgNFt7Y0G40x, expense_description=Pizza, expense_date=2019-09-10, cost=51.81, approved=true, link_to_member=recD078PnS3x2doBe, link_to_budget=recwXIiKoBMjXJsGZ
expense: expense_id=rec4Zg7WEmfiHXcnC, expense_description=Posters, expense_date=2019-10-10, cost=67.81, approved=true, link_to_member=rec4BLdZHS2Blfp4v, link_to_budget=recsI0IzpUuxl2bPh
expense: expense_id=rec7gUiykKKW4RaJS, expense_description=Parking, expense_date=2019-11-19, cost=6.0, approved=true, link_to_member=recro8T1MPMwRadVH, link_to_budget=recTUGXxhTaFZ2qkg
expense: expense_id=recBqNAd2axwvbSUd, expense_description=Water, Cookies, expense_date=2019-09-10, cost=20.2, approved=true, link_to_member=recro8T1MPMwRadVH, link_to_budget=recZAjcliIUo4BCKW
expense: expense_id=recHPdtBtpThSA9lq, expense_description=Pizza, expense_date=2019-10-22, cost=92.82, approved=true, link_to_member=recD078PnS3x2doBe, link_to_budget=recr60T1tLsfdICV8
expense: expense_id=recILV3eykJuWc489, expense_description=Pizza, expense_date=2019-11-19, cost=62.6, approved=true, link_to_member=recD078PnS3x2doBe, link_to_budget=reczf4LoOK6z7oOec
expense: expense_id=recIudsuLiDpzK8Io, expense_description=Posters, expense_date=2019-09-01, cost=54.25, approved=NULL, link_to_member=recD078PnS3x2doBe, link_to_budget=recMc8TbR76rmUSHG
expense: expense_id=recJnyr7Z1CjAlHgA, expense_description=Posters, expense_date=2019-10-01, cost=54.25, approved=true, link_to_member=recD078PnS3x2doBe, link_to_budget=recTxecmwIhCdIKvl
income: income_id=rec0s9ZrO15zhzUeE, date_received=2019-10-17, amount=50, source=Dues, notes=NULL, link_to_member=reccW7q1KkhSKZsea
income: income_id=rec7f5XMQZexgtQJo, date_received=2019-09-04, amount=50, source=Dues, notes=NULL, link_to_member=recTjHY5xXhvkCdVT
income: income_id=rec8BUJa8GXUjiglg, date_received=2019-10-08, amount=50, source=Dues, notes=NULL, link_to_member=recUdRhbhcEO1Hk5r
income: income_id=rec8V9BPNIoewWt2z, date_received=2019-10-02, amount=50, source=Dues, notes=NULL, link_to_member=rec3pH4DxMcWHMRB7
income: income_id=recCRWMfFqifuKMc6, date_received=2019-09-18, amount=50, source=Dues, notes=NULL, link_to_member=rec28ORZgcm1dtqBZ
income: income_id=recMCFQxAiJXxrbsG, date_received=2019-10-31, amount=50, source=Dues, notes=NULL, link_to_member=recZN8afUWlE5fZHG
income: income_id=recMFy9sJHhuPZ4cz, date_received=2019-09-25, amount=50, source=Dues, notes=NULL, link_to_member=recjHj4BS5A541n9v
income: income_id=recN3WFwGR0c17xe2, date_received=2019-09-14, amount=200, source=Fundraising, notes=Secured donations to help pay for spe..., link_to_member=NULL
income: income_id=recOo362sJrXFv2az, date_received=2019-09-25, amount=50, source=Dues, notes=NULL, link_to_member=recL94zpn6Xh6kQii
income: income_id=recPG7h3YcEJpddEW, date_received=2019-09-16, amount=50, source=Dues, notes=NULL, link_to_member=recro8T1MPMwRadVH
zip_code: zip_code=501, type=Unique, city=Holtsville, county=Suffolk County, state=New York, short_state=NY
zip_code: zip_code=544, type=Unique, city=Holtsville, county=Suffolk County, state=New York, short_state=NY
zip_code: zip_code=601, type=Standard, city=Adjuntas, county=Adjuntas Municipio, state=Puerto Rico, short_state=PR
zip_code: zip_code=602, type=Standard, city=Aguada, county=Aguada Municipio, state=Puerto Rico, short_state=PR
zip_code: zip_code=603, type=Standard, city=Aguadilla, county=Aguadilla Municipio, state=Puerto Rico, short_state=PR
zip_code: zip_code=604, type=PO Box, city=Aguadilla, county=NULL, state=Puerto Rico, short_state=PR
zip_code: zip_code=605, type=PO Box, city=Aguadilla, county=NULL, state=Puerto Rico, short_state=PR
zip_code: zip_code=606, type=Standard, city=Maricao, county=Maricao Municipio, state=Puerto Rico, short_state=PR
zip_code: zip_code=610, type=Standard, city=Anasco, county=Anasco Municipio, state=Puerto Rico, short_state=PR
zip_code: zip_code=611, type=PO Box, city=Angeles, county=NULL, state=Puerto Rico, short_state=PR

Complete distinct values for the short enumerable text columns:
member.position: Inactive, Member, President, Secretary, Treasurer, Vice President
event.type: Budget, Community Service, Election, Game, Guest Speaker, Meeting, Registration, Social
event.status: Closed, Open, Planning
budget.event_status: Closed, Open, Planning
budget.category: Advertisement, Club T-Shirts, Food, Parking, Speaker Gifts
expense.approved: true, NULL
income.source: Dues, Fundraising, School Appropration, Sponsorship
member.t_shirt_size: Large, Medium, Small, X-Large
zip_code.type: PO Box, Standard, Unique

Numeric and date ranges:
expense.cost: min=6.0, max=295.12, avg=65.19
budget.amount: min=10, max=350, avg=80.77
budget.spent: min=0.0, max=327.07, avg=40.12
budget.remaining: min=-24.25, max=150.0, avg=40.65
income.amount: min=50, max=3000, avg=162.5
event.event_date: min=2019-09-01T07:00:00, max=2020-05-05T12:00:00
expense.expense_date: min=2019-08-20, max=2019-11-19
income.date_received: min=2019-09-01, max=2019-10-31
