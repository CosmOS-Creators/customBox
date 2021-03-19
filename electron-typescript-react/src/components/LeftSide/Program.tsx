import { Collapse, ListItem, ListItemText, makeStyles, TextField } from '@material-ui/core'
import { ExpandLess, ExpandMore } from '@material-ui/icons'
import React from 'react'
import Task from './Task';

const useStyles = makeStyles((theme) => ({
    root: {
      marginTop:10,
      width: '100%',
      backgroundColor: "#464657",
      color: "#fff",
      borderRadius:"15px",
      fontWeight: 'bold',
      fontFamily:'Montserrat, sans-serif'
    },
    program: {
      paddingLeft: theme.spacing(4),
    },
    task: {
        paddingLeft: theme.spacing(8),
      },
    coreInput: {
        backgroundColor:'transparent',
        padding:15,
        borderRadius:20,
        fontSize:14,
        color:"#fff",
        border:'solid 0.5px',
        borderColor:'#636970',
    }
  }));

interface ProgramProps {
    coreOpen:boolean;
}

const Program:React.FC<ProgramProps> = ({coreOpen}) => {
    const classes = useStyles();
    const [programOpen, setProgramOpen] = React.useState(false)

    return (
        <>
          <div style={{display:'flex', flexDirection:'column'}}>
          <label style={{color:"#fff", marginLeft:'2rem', marginRight:'1rem', marginBottom:5, fontFamily:'Montserrat, sans-serif'}}>Enter the name of the core</label>
          <input type="text" style={{marginLeft:"1rem", marginRight:'1rem'}} className={classes.coreInput} placeholder="Core name"/>
          </div>
        <ListItem button className={classes.program} onClick={()=>setProgramOpen(!programOpen)}>
          <ListItemText primary="Program" />
        </ListItem>
        <ListItem className={classes.task} button >
          <ListItemText primary="Task" />
        </ListItem>
        {/* <Task programOpen={programOpen}/> */}
        </>
    )
}

export default Program
