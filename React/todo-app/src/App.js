import React, {useState, useEffect} from 'react'
import api from './api'

const App = () => {
  // gets object and setter function
  const [item, setItem] = useState([]);

  const [formData, setFormData] = useState({
    title: '',
    desc: '',
    priority: '',
    complete: false
  });

  // sets todo item to user's input
  const fetchItems = async () => {
    const response = await api.get('/todos/');
    setItem(response.data)
  };

  // useState allows us to keep state within React, let's us know
  // when to shift pieces of data

  // useEffect fetches the api input at run time
  useEffect(() => {
    fetchItems();
  }, []);

  // upon checking off checkbox, complete will be set to its opposite value
  const handleInputChange = (event) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setFormData({
      ...formData, 
      [event.target.name]: value,
    });
  };

  // overriding default form submitting, inputs will be reset on submit
  const handleFormSubmit = async (event) => {
    event.preventDefault();
    await api.post('/todos/', formData)
    fetchItems();
    setFormData({
      title: '',
      desc: '',
      priority: '',
      complete: false
    });
  };

  return (
    <div>
      <nav className = 'navbar navbar-dark bg-primary'>
        <div className = 'container-fluid'>
          <a className='navbar-brand' href="#">
            TodoList App
          </a>
        </div>
      </nav>

      
      <div className='container'>
        <form onSubmit={handleFormSubmit}>
          
          <div className='mb-3 mt-3'>
            <label htmlFor='title' className='form-label'>
              Title
            </label>
            <input type='text' className='form-control' id='title' name='title' onChange={handleInputChange} value={formData.title}/>
          </div>
          
          <div className='mb-3'>
            <label htmlFor='description' className='form-label'>
              Short Description or Notes
            </label>
            <input type='text' className='form-control' id='desc' name='desc' onChange={handleInputChange} value={formData.desc}/>
          </div>
          
          <div className='mb-3'>
            <label htmlFor='priority' className='form-label'>
              Priority (Low, Medium, High)
            </label>
            <input type='text' className='form-control' id='priority' name='priority' onChange={handleInputChange} value={formData.priority}/>
          </div>
          
          <div className='mb-3'>
            <label htmlFor='complete' className='form-label'>
              Complete?
            </label>
            <input type='checkbox' id='complete' name='complete' onChange={handleInputChange} value={formData.complete}/>
          </div>

          <button type='submit' className='btn btn-primary'>
            Submit
          </button>
        </form>

        <table className='table table-striped table-bordered table-hover mt-3 mb-3'>
        <thead>
          <tr>
            <th>Title</th>
            <th>Description</th>
            <th>Priority</th>
            <th>Completed</th>
          </tr>
        </thead>
        <tbody>
          {
            item.map((i) => (
              <tr key={i.id}>
                <td>{i.title}</td>
                <td>{i.desc}</td>
                <td>{i.priority.toUpperCase()}</td>
                <td>{i.complete ? 'Yes' : 'No'}</td>
              </tr>
            ))
          }
        </tbody>

        </table>
      </div>  



    </div>
  )
}


export default App;
