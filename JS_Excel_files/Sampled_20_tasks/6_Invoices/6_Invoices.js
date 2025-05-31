$("#run").on("click", () => tryCatch(run));

async function run() {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const salesRange = sheet.getRange("G2:G19");
    
    const averageSales = salesRange.getAverage();
    const conditionalFormat = salesRange.conditionalFormats.add(Excel.ConditionalFormatType.cellValue);
    
    conditionalFormat.cellValue.format.fill.color = "red";
    conditionalFormat.cellValue.rule = {
      formula1: averageSales,
      operator: "GreaterThan"
    };

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