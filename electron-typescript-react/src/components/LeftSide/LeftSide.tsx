import { Collapse, List, ListItem, ListItemIcon, ListItemText, ListSubheader, makeStyles } from '@material-ui/core';
import React from 'react'
import InboxIcon from '@material-ui/icons/MoveToInbox';
import DraftsIcon from '@material-ui/icons/Drafts';
import SendIcon from '@material-ui/icons/Send';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import StarBorder from '@material-ui/icons/StarBorder';
import Program from './Program';
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
  }));
  

const Navigation = () => {
    const classes = useStyles();
  const [open, setOpen] = React.useState(true);
  const [programOpen, setProgramOpen] = React.useState(false)
  const [coreOpen, setCoreOpen] = React.useState(false)
  const [taskOpen, setTaskOpen] = React.useState(false)

  const handleClick = () => {
    setOpen(!open);
  };
    return (
        <>
        <div>
            <h2 style={{color:"#fff", padding:"1rem"}}>Create new core</h2>
        </div>
             <List
      component="nav"
      aria-labelledby="nested-list-subheader"
      className={classes.root}
    >
      <ListItem button onClick={()=>setCoreOpen(!coreOpen)}>
        <ListItemText primary="Core" />
        {coreOpen ? <ExpandLess /> : <ExpandMore />}
      </ListItem>
      <Program coreOpen={coreOpen}/>
     
    </List>
    </>
    )
}

export default Navigation
