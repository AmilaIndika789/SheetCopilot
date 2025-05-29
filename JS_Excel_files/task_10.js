$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    let sheets = context.workbook.worksheets;
    let sheet1 = sheets.getItem("Sheet1");

    sheet1.load("position"); // Load the position of Sheet1

    await context.sync(); // Sync before using loaded properties

    // Add a new sheet
    let sheet2 = sheets.add("Sheet2");
    sheet2.position = sheet1.position; // Insert before Sheet1

    // Copy headers
    let headers = sheet1.getRange("A1:E1");
    sheet2.getRange("A1:E1").copyFrom(headers);

    // Copy remaining 9 rows
    let remainingNineRows = sheet1.getRange("A2:E10");
    sheet2.getRange("A2:E10").copyFrom(remainingNineRows);

    await context.sync();
  }).catch((error) => {
    console.error(error);
  });
}

/** Default helper for invoking an action and handling errors. */
async function tryCatch(callback) {
  try {
    await callback();
  } catch (error) {
    // Note: In a production add-in, you'd want to notify the user through your add-in's UI.
    console.error(error);
  }
}
