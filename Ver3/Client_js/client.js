const url_dispatching = "http://127.0.0.1:8000/api/v1.1/control/fans?farm_id=1"
const data = {'time': '1682656256', 'co2': 9876}
const url_dispatching_option = 
{
    "method": "POST",
    "headers": 
    {
        "content-Type": "application/json",
    },
    "body": JSON.stringify(data)
}

const test_func = async ()=>
{
    response = await fetch(url_dispatching, url_dispatching_option)
    response_data = await response.json()
    console.log(response_data)
}

test_func()

