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
        borderRadius:10,
        fontSize:18,
        color:"#fff"
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
        <Collapse in={coreOpen} timeout="auto" unmountOnExit>
        <input type="text" style={{marginLeft:"1rem"}} className={classes.coreInput} placeholder="Core name"/>
        <ListItem button className={classes.program} onClick={()=>setProgramOpen(!programOpen)}>
          <ListItemText primary="Program" />
          {programOpen ? <ExpandLess /> : <ExpandMore />}
        </ListItem>
        </Collapse>
        <Task programOpen={programOpen}/>
        </>
    )
}

export default Program
