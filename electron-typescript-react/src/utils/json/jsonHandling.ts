import fs from 'fs'

export const createJSON = (initialData: any) => {
    const data = JSON.stringify(initialData, null, 4);
    fs.writeFile('/Users/michalzaduban/Desktop/Cosmos/cosmos_customBox/electron-typescript-react/src/output/outputJson.json', data, (err) => {
        if (err) {
            throw err;
        }
        console.log("JSON data is saved.");
    });
}

export const readJSON = (pathToJson: string) => {
    return fs.readFile(pathToJson, 'utf-8', (err, data) => {
        if (err) {
            throw err;
        }
        const user = JSON.parse(data.toString());
        console.log(user);
        return user
    });
}

