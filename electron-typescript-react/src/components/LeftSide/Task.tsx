import { makeStyles, Collapse, ListItem, ListItemText } from '@material-ui/core';
import { ExpandLess, ExpandMore } from '@material-ui/icons';
import React from 'react'

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
  }));

interface TaskProps {
    programOpen:boolean;
}

const Task:React.FC<TaskProps> = ({programOpen}) => {
    const classes = useStyles();
    const [taskOpen, setTaskOpen] = React.useState(false)

    return (
        <Collapse in={programOpen} timeout="auto" unmountOnExit>
        <ListItem className={classes.task} button onClick={()=>setTaskOpen(!taskOpen)}>
          <ListItemText primary="Task" />
          {taskOpen ? <ExpandLess /> : <ExpandMore />}
        </ListItem>
        </Collapse>
    )
}

export default Task
