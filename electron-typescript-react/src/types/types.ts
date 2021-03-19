export interface Core {
    name: string;
    programs?: Program[] | undefined | null;
    scheduler?: Scheduler;
}

export interface Program {
    name: string;
    tasks?: Task[] | undefined | null
}

export interface Task {
    name: string;
    wcet: number;
    period: number;
    stack_size: number;
}


export interface Scheduler {
    hyperTick: number;
    sync: boolean;
    syncPeriod: number;
    table?: Table[] | undefined | null
}

export interface Table {
    core: number;
    program: number;
    task: number;
    executionTick: number;
}