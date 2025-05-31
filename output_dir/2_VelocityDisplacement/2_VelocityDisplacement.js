$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getUsedRange();
    
    // Load the values from the range
    range.load("values");
    await context.sync();

    // Calculate time and store in a new array
    const timeValues = range.values.slice(1).map(row => {
      const displacement = row[0];
      const velocity = row[1];
      return velocity !== 0 ? [displacement / velocity] : [null]; // Avoid division by zero
    });

    // Add a new column header for "Time s"
    const timeHeaderRange = sheet.getRange("C1");
    timeHeaderRange.values = [["Time s"]];

    // Write the calculated time values to the new column
    const timeRange = sheet.getRange(`C2:C${timeValues.length + 1}`);
    timeRange.values = timeValues;

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