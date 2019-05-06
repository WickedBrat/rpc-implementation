let proxy = require('./stub/main');
let str = 'Ayush yyy';
let num = 4;
async function main() {
    let addResult = await proxy.callProcedure('add', 'number', 4, 1);
    console.log('Addition result => ' + addResult);
    let subResult = await proxy.callProcedure('sub', 'number', 3, 5);
    console.log('Subtraction result => ' + subResult);
    let mulResult = await proxy.callProcedure('mul', 'number', 1, 2);
    console.log('Multiplication result => ' + mulResult);
}
main();