import React from 'react'
import { render } from 'react-dom'
import { GlobalStyle } from './styles/GlobalStyle'

import Greetings from './components/Greetings'
import LeftSide from './components/LeftSide/LeftSide'
import RightSide from './components/RightSide/RightSide'
import { Grid } from '@material-ui/core'

const mainElement = document.createElement('div')
mainElement.setAttribute('id', 'root')
document.body.appendChild(mainElement)

const App = () => {
  return (
    <>  
      <Grid container spacing={3} style={{backgroundColor:"#202025", height:"100vh"}}>
        <Grid item xs={6}>
        <LeftSide/>
        </Grid>
        <Grid item xs={6}>
        <RightSide/>
        </Grid>
      </Grid>
    </>
  )
}

render(<App />, mainElement)
