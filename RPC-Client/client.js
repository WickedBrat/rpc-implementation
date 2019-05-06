let proxy = require('./stub/main');
let str = "Ayush yyy";
let num = 4;

async function main() {
  let addResult = await add(4, 1);
  console.log("Addition result => " + addResult);

  let subResult = await sub(3, 5);
  console.log("Subtraction result => " + subResult);

  let mulResult = await mul(1, 2);
  console.log("Multiplication result => " + mulResult);
   //let resultCount = await find_count(str, 'y');
   //let resultEven = await is_even(num);

   //console.log(resultEven);
}

main();