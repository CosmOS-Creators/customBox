import React from 'react'
import { render } from 'react-dom'
import { GlobalStyle } from './styles/GlobalStyle'

import Greetings from './components/Greetings'
import LeftSide from './components/LeftSide/LeftSide'
import RightSide from './components/RightSide/RightSide'
import { Grid } from '@material-ui/core'
import { Core } from './types/types'
// import {createStore} from 'react-redux'

// const store = createStore(rootReducer)

const mainElement = document.createElement('div')
mainElement.setAttribute('id', 'root')
document.body.appendChild(mainElement)

const cores:Core[] = []

export const CoresContext = React.createContext({cores:cores});



const App = () => {
  return (
    <>  
    <CoresContext.Provider value={{cores:cores}}>
      <Grid container spacing={3} style={{backgroundColor:"#131214", height:"100vh"}}>
        <Grid item xs={5}>
        <LeftSide/>
        </Grid>
        <Grid item xs={7}>
        <RightSide/>
        </Grid>
      </Grid>
      </CoresContext.Provider >
    </>
  )
}

render(<App />, mainElement)
