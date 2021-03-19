import {
  Button,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  makeStyles,
  Typography,
} from '@material-ui/core';
import * as React from 'react';
import InboxIcon from '@material-ui/icons/MoveToInbox';
import DraftsIcon from '@material-ui/icons/Drafts';
import Program from './Program';
import Task from './Task';
import { Core } from '../../types/types';
import { CoresContext } from '../../App';
import { createJSON } from '../../utils/json/jsonHandling';

const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: 10,
    width: '100%',
    backgroundColor: '#464657',
    color: '#fff',
    borderRadius: '15px',
    fontWeight: 'bold',
    fontFamily: 'Montserrat, sans-serif',
  },
  program: {
    paddingLeft: theme.spacing(4),
  },
  task: {
    paddingLeft: theme.spacing(8),
  },
  coreInput: {
    backgroundColor: 'transparent',
    padding: 15,
    borderRadius: 20,
    fontSize: 14,
    color: '#fff',
    border: 'solid 0.5px',
    borderColor: '#636970',
  },
}));

const Navigation = () => {
  const classes = useStyles();
  const coresContext = React.useContext(CoresContext);
  //const [core, setCore] = useRecoilState(coreState);
  const [core, setCore] = React.useState<any>();
  const [coreName, setCoreName] = React.useState<string>('');
  const [programName, setProgramName] = React.useState<string>('');
  const [taskName, setTaskName] = React.useState<string>('');
  const [open, setOpen] = React.useState(true);

  const createCore = () => {
    const core: Core = {
      name: coreName,
      programs: [
        {
          name: programName,
          tasks: [
            {
              name: taskName,
              wcet: 0,
              period: 0,
              stack_size: 0,
            },
          ],
        },
      ],
    };
    coresContext.cores = [...coresContext.cores, core];
    setCore(core);
    createJSON(core);
    console.log('Context from function', core);
  };

  const handleClick = () => {
    setOpen(!open);
  };

  React.useEffect(() => {});
  return (
    <>
      <div>
        <h2 style={{ color: '#fff', paddingLeft: 10 }}>CORES</h2>
      </div>
      <Button
        variant="contained"
        style={{ backgroundColor: '#004aad', color: '#fff', borderRadius: 10 }}
      >
        Add new core
      </Button>
      <List
        component="nav"
        aria-labelledby="nested-list-subheader"
        className={classes.root}
      >
        <ListItem button>
          <ListItemText
            primary="Core"
            style={{ fontFamily: 'Montserrat, sans-serif' }}
          />
        </ListItem>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <label
            style={{
              color: '#fff',
              marginLeft: '2rem',
              marginRight: '1rem',
              marginBottom: 5,
              fontFamily: 'Montserrat, sans-serif',
            }}
          >
            Enter the name of the core
          </label>
          <input
            type="text"
            style={{ marginLeft: '1rem', marginRight: '1rem' }}
            className={classes.coreInput}
            placeholder="Core name"
            onChange={(e) => setCoreName(e.target.value)}
          />
        </div>
        <ListItem button>
          <ListItemText primary="Program" />
        </ListItem>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <label
            style={{
              color: '#fff',
              marginLeft: '2rem',
              marginRight: '1rem',
              marginBottom: 5,
              fontFamily: 'Montserrat, sans-serif',
            }}
          >
            Enter the name program
          </label>
          <input
            type="text"
            style={{ marginLeft: '1rem', marginRight: '1rem' }}
            className={classes.coreInput}
            placeholder="Program name"
            onChange={(e) => setProgramName(e.target.value)}
          />
        </div>
        <ListItem
          button
          onClick={() => {
            createCore();
            console.log(
              'States',
              coreName,
              programName,
              taskName,
              'Context',
              coresContext
            );
          }}
        >
          <ListItemText primary="Task" />
        </ListItem>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <label
            style={{
              color: '#fff',
              marginLeft: '2rem',
              marginRight: '1rem',
              marginBottom: 5,
              fontFamily: 'Montserrat, sans-serif',
            }}
          >
            Enter the name of the task
          </label>
          <input
            type="text"
            style={{ marginLeft: '1rem', marginRight: '1rem' }}
            className={classes.coreInput}
            placeholder="Task name"
            onChange={(e) => setTaskName(e.target.value)}
          />
        </div>
      </List>
      <Button
        variant="contained"
        style={{
          backgroundColor: '#004aad',
          color: '#fff',
          borderRadius: 10,
          margin: 10,
        }}
        onClick={() => {
          createCore();
          console.log('Cores from context', core);
        }}
      >
        Create JSON file
      </Button>
      <Typography style={{ color: '#fff' }}>{JSON.stringify(core)}</Typography>
    </>
  );
};

export default Navigation;
