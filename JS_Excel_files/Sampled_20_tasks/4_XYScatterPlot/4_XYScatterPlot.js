$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getRange("B2:B38"); // Range column
    const markedAnglesRange = sheet.getRange("D2:D38"); // Marked Angles column

    range.load("values"); // Load values from the Range column
    await context.sync();

    const values = range.values;
    const markedAnglesValues = values.map(row => (row[0] > 0.5 ? ['+'] : ['']));

    markedAnglesRange.values = markedAnglesValues; // Write '+' or leave unchanged
    await context.sync();
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